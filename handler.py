from json import load
from pandas import DataFrame, concat, read_csv, read_sql, Series
from sqlite3 import connect
from rdflib import Graph, URIRef, RDF, Namespace, Literal
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from sparql_dataframe import get


class Handler(object):
    def __init__(self):
        self.dbPathOrUrl = ""

    def getDbPathOrUrl(self):
        return self.dbPathOrUrl

    def setDbPathOrUrl(self, new_path_or_url):
        if type(new_path_or_url) == str:
            self.dbPathOrUrl = new_path_or_url
            return self.dbPathOrUrl == new_path_or_url
        else:
            return False


class UploadHandler(Handler):
    def __init__(self):
        super().__init__()

    def pushDataToDb(self):
        pass


class ProcessDataUploadHandler(UploadHandler):
    def __init__(self):
        super().__init__()

    def pushDataToDb(self, json_file: str) -> bool:

        # creating a dataframe with the activities as columns and the objects as rows
        with open(json_file) as f:
            list_of_dict = load(f)
            keys = list_of_dict[0].keys()
            j_df = DataFrame(list_of_dict, columns=keys)
            j_df = j_df.drop_duplicates(
                subset="object id", keep="first"
            )  # removing all duplicates from the dataframe

            # creating empty dataframes with the correct column names for each activity.
            df_dict = {}
            for column_name in j_df.columns.to_list():  # iterating over the columns to cretate the activity dataframes
                cell = j_df.loc[0, column_name]
                if type(cell) == dict:
                    keys = cell.keys()
                    df_dict[column_name] = DataFrame(columns=keys)
                    df_dict[column_name]["object id"] = []  # adding the object id column
                    df_dict[column_name].insert(0, "internal Id", [])  # adding the internal id column

            # populating each empty activity dataframe with the correct information from j_df
            for df_name, df in df_dict.items():
                for column_to_fill in df.columns.to_list()[1:-1]:
                    int_ids = []
                    content = []
                    ob_ids = []
                    num_rows = len(j_df)
                    i = 0
                    while i < num_rows:
                        ob_id = j_df.loc[i]["object id"]
                        cell = j_df.loc[i][df_name]
                        column_value = cell[column_to_fill]

                        if type(column_value) == list:
                            column_value = ", ".join(column_value)
                        elif column_value == "":
                            column_value = None

                        int_ids.append(f"{df_name}-{ob_id}")
                        ob_ids.append(ob_id)
                        content.append(column_value)

                        i += 1

                    df["internal Id"] = int_ids
                    df["object id"] = ob_ids
                    df[column_to_fill] = content

            # correcting the tables and the columns names
            table_dict = {}
            for df_name, df in df_dict.items():
                table_dict[df_name[0].upper() + df_name[1:]] = df

                new_columns = []
                for column_name in df.columns.tolist():
                    new_name = column_name.title()
                    new_name = new_name.replace(" ", "")
                    new_name = new_name[0].lower() + new_name[1:]
                    new_columns.append(new_name)
                df.columns = new_columns

            # uploading the tables to the database
            with connect(self.dbPathOrUrl) as con:
                for table_name, table in table_dict.items():
                    exists_query = f'SELECT name FROM sqlite_master WHERE type="table" AND name="{table_name}"'
                    exists = con.execute(exists_query).fetchone()

                    if (
                        exists
                    ):  # if the table already exists, if present, the duplictaes get removed and the table is uploaded
                        unic_id_col = table.columns[0]
                        unic_id_query = f'SELECT "{unic_id_col}" FROM "{table_name}"'
                        unic_ids_db_raw = con.execute(unic_id_query).fetchall()

                        unic_ids_db = set()
                        for item in unic_ids_db_raw:
                            unic_ids_db.add(item[0])

                        unic_ids_table = set(table[table.columns.tolist()[0]].tolist())
                        no_dup_ids = unic_ids_table - unic_ids_db
                        no_dup_table = table[table["internalId"].isin(no_dup_ids)]

                        no_dup_table.to_sql(
                            table_name,
                            con,
                            if_exists="append",
                            index=False,
                            dtype="string",
                        )

                    else:
                        table.to_sql(table_name, con, if_exists="replace", index=False)

            # applying a simple control to verify the correct upload of the tables
            control_query = "SELECT name FROM sqlite_master WHERE type = 'table'"
            table_names_db_raw = con.execute(control_query).fetchall()
            table_names_db = set()
            for item in table_names_db_raw:
                table_names_db.add(item[0])

            table_names = set()
            for table_name, table in table_dict.items():
                table_names.add(table_name)

            if table_names_db == table_names:
                return True
            else:
                False


# The class for uploading the csv file to a graph database
class MetadataUploadHandler(UploadHandler): # Simone
    def pushDataToDb(self, path: str) -> bool:

        # storing the number of triples already present in the database
        endpoint = self.dbPathOrUrl + "sparql"

        query = """
        SELECT ?s ?p ?o
        WHERE {
            ?s ?p ?o .
        }
        """
        df_database_before = get(endpoint, query, True)

        n_triples_in_database_before = 0
        for idx, row in df_database_before.iterrows():
            n_triples_in_database_before += 1

        # putting all the people URIs and IDS already present in the database in two dictionaries
        people_authority_ids = dict()
        people_object_ids = dict()
        people_number = 0

        query = """
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix schema: <http://schema.org/>
        SELECT ?personURI ?personId
        WHERE {
            ?personURI rdf:type schema:Person .
            ?personURI schema:identifier ?personId .
        }
        """
        df_people = get(endpoint, query, True)

        for indx, row in df_people.iterrows():
            people_authority_ids[str(row["personId"])] = URIRef(row["personURI"])
            people_number += 1

        # putting all the cultural object URIs and IDs already present in the database in one dictionary
        object_uris = dict()
        object_number = 0

        query = """
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        prefix schema: <http://schema.org/>
        SELECT ?culturalObjectURI ?culturalObjectId
        WHERE {
            ?culturalObjectURI rdf:type ?type .
            FILTER(?type != schema:Person)
            ?culturalObjectURI schema:identifier ?culturalObjectId .
        }
        """
        df_objects = get(endpoint, query, True)

        for indx, row in df_objects.iterrows():
            object_uris[str(row["culturalObjectId"])] = URIRef(row["culturalObjectURI"])
            object_number += 1

        # defining namespaces
        schema = Namespace("http://schema.org/")
        github = Namespace("https://breaking-data.github.io/Data-Science-Project/")

        # creating the graph
        metadata_graph = Graph()
        metadata_graph.bind("schema", schema)
        metadata_graph.bind("github", github)

        # attribute related to the IdentifiableEntity class
        identifier = URIRef(schema.identifier)

        # attributes related to the CulturalHeritageObject class
        title = URIRef(schema.title)
        date = URIRef(schema.dateCreated)
        owner = URIRef(github.owner)
        place = URIRef(schema.itemLocation)

        # relations among classes
        hasAuthor = URIRef(schema.author)

        # attributes related to the Person class
        name = URIRef(schema.name) 

        # classes of resources
        Person = URIRef(schema.Person)
        NauticalChart = URIRef(github.NauticalChart)
        ManuscriptPlate = URIRef(github.ManuscriptPlate)
        ManuscriptVolume = URIRef(github.ManuscriptVolume)
        PrintedVolume = URIRef(github.PrintedVolume)
        PrintedMaterial = URIRef(github.PrintedMaterial)
        Herbarium = URIRef(github.Herbarium)
        Specimen = URIRef(github.Specimen)
        Painting = URIRef(github.Painting)
        Model = URIRef(github.Model)
        Map = URIRef(schema.Map)

        # the process of populating the local graph
        metadata_frame = read_csv(
            path,
            keep_default_na=False,
            dtype={
                "Id": "string",
                "Type": "string",
                "Title": "string",
                "Date": "string",
                "Author": "string",
                "Owner": "string",
                "Place": "string",
            },
        )

        base_url = "https://breaking-data.github.io/Data-Science-Project/"

        # populating the local graph with all the people
        for idx, row in metadata_frame.iterrows():
            author = row["Author"]
            if author != "":
                list_of_authors = author.split(";")
                for a in list_of_authors:
                    a_stripped = a.strip()
                    
                    # Here I'm isolating the authority identifier and the name of the author
                    indx_for_split = a_stripped.index("(")
                    person_name = a_stripped[: indx_for_split - 1]
                    person_id = a_stripped[(indx_for_split + 1) : -1]
                    object_id = row["Id"]

                    # Checking if the person is already in the dictionaries
                    if person_id in people_authority_ids.keys():
                        person_uri = people_authority_ids[person_id]
                        if object_id in people_object_ids.keys():
                            people_object_ids[object_id].append(person_uri)
                        else:
                            people_object_ids[object_id] = [person_uri]

                    else:
                        local_id = "person-" + str(people_number)
                        subj = URIRef(base_url + local_id)

                        # Adding to the graph the type Person, the identifier and the name of the person
                        metadata_graph.add((subj, RDF.type, Person))
                        metadata_graph.add((subj, identifier, Literal(person_id)))
                        metadata_graph.add((subj, name, Literal(person_name)))

                        people_authority_ids[person_id] = subj
                        if object_id in people_object_ids.keys():
                            people_object_ids[object_id].append(subj)
                        else:
                            people_object_ids[object_id] = [subj]

                        people_number += 1

        # populating the graph with all the cultural heritage objects
        for idx, row in metadata_frame.iterrows():
            if row["Id"] not in object_uris:
                local_id = "culturalobject-" + str(object_number)
                subj = URIRef(base_url + local_id)

                if row["Type"] != "":
                    if row["Type"].lower() == "nautical chart":
                        metadata_graph.add((subj, RDF.type, NauticalChart))

                    elif row["Type"].lower() == "manuscript plate":
                        metadata_graph.add((subj, RDF.type, ManuscriptPlate))

                    elif row["Type"].lower() == "manuscript volume":
                        metadata_graph.add((subj, RDF.type, ManuscriptVolume))

                    elif row["Type"].lower() == "printed volume":
                        metadata_graph.add((subj, RDF.type, PrintedVolume))

                    elif row["Type"].lower() == "printed material":
                        metadata_graph.add((subj, RDF.type, PrintedMaterial))

                    elif row["Type"].lower() == "herbarium":
                        metadata_graph.add((subj, RDF.type, Herbarium))

                    elif row["Type"].lower() == "specimen":
                        metadata_graph.add((subj, RDF.type, Specimen))

                    elif row["Type"].lower() == "painting":
                        metadata_graph.add((subj, RDF.type, Painting))

                    elif row["Type"].lower() == "model":
                        metadata_graph.add((subj, RDF.type, Model))

                    elif row["Type"].lower() == "map":
                        metadata_graph.add((subj, RDF.type, Map))
                    else:
                        print(
                            f"The type of the object with id {row['Id']} is not compliant with the data model. The object will not be added to the graph."
                        )
                        continue

                if row["Id"] != "":
                    metadata_graph.add((subj, identifier, Literal(row["Id"])))
                if row["Title"] != "":
                    metadata_graph.add((subj, title, Literal(row["Title"])))
                if row["Date"] != "":
                    metadata_graph.add((subj, date, Literal(row["Date"])))
                if row["Owner"] != "":
                    metadata_graph.add((subj, owner, Literal(row["Owner"])))
                if row["Place"] != "":
                    metadata_graph.add((subj, place, Literal(row["Place"])))
                if row["Author"] != "":
                    authors = people_object_ids[row["Id"]]
                    for a in authors:
                        metadata_graph.add((subj, hasAuthor, a))

                object_number += 1

        # sending the graph to the database
        store = SPARQLUpdateStore()

        store.open((endpoint, endpoint))

        for triple in metadata_graph.triples((None, None, None)):
            store.add(triple)

        store.close()

        # checking if the graph was uploaded correctly
        query = """
        SELECT ?s ?p ?o
        WHERE {
            ?s ?p ?o .
        }
        """
        df_database_after = get(endpoint, query, True)

        n_triples_in_graph = len(metadata_graph)
        n_triples_in_database_after = 0
        for idx, row in df_database_after.iterrows():
            n_triples_in_database_after += 1

        return (
            n_triples_in_database_after
            == n_triples_in_graph + n_triples_in_database_before
        )


class QueryHandler(Handler):
    def getById(self, id: str) -> DataFrame:
        if "http" in self.getDbPathOrUrl():
            db_address = self.getDbPathOrUrl()
        else:
            return DataFrame()

        endpoint = db_address + "sparql"
        query = "PREFIX schema: <http://schema.org/>"
        if ":" in id:
            query += (
                """
                SELECT ?uri ?name
                WHERE {
                    ?uri schema:identifier "%s" .
                    ?uri schema:name ?name .
                    ?uri schema:identifier ?id .
                }
                """
                % id
            )
        else:
            query += (
                """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX github: <https://breaking-data.github.io/Data-Science-Project/>

                SELECT ?obj ?type ?title ?date ?owner ?place ?author
                WHERE {
                ?obj schema:identifier "%s" .
                ?obj rdf:type ?type .
                ?obj schema:title ?title .
                ?obj github:owner ?owner .
                ?obj schema:itemLocation ?place .
                OPTIONAL {
                    ?obj schema:author ?author .
                    }
                OPTIONAL { 
                    ?obj schema:dateCreated ?date .
                    }
                }
                """
                % id
            )
        df_entity = get(endpoint, query, True)

        return df_entity


class MetadataQueryHandler(QueryHandler):
    query_header = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX schema: <http://schema.org/>
    PREFIX github: <https://breaking-data.github.io/Data-Science-Project/>
    """

    # it returns a data frame containing all the people included in the database.
    def getAllPeople(self) -> DataFrame:
        endpoint = self.getDbPathOrUrl() + "sparql"
        query = (
            self.query_header
            + """
        SELECT ?uri ?name ?id
        WHERE {
            ?uri rdf:type schema:Person .
          	?uri schema:name ?name .
            ?uri schema:identifier ?id .
        }
        """
        )
        df_people = get(endpoint, query, True)
        return df_people

    # it returns a data frame with all the cultural heritage objects described in it.
    def getAllCulturalHeritageObjects(self) -> DataFrame:
        endpoint = self.getDbPathOrUrl() + "sparql"
        query = (
            self.query_header
            + """
        SELECT ?uri ?type ?id ?title ?date ?owner ?place ?author
        WHERE {
            ?uri rdf:type ?type .
            FILTER (?type != schema:Person)
            ?uri schema:identifier ?id .
            ?uri schema:title ?title .
            ?uri github:owner ?owner .
            ?uri schema:itemLocation ?place .
            OPTIONAL {
                ?uri schema:author ?author .
                
            }
            OPTIONAL {
                ?uri schema:dateCreated ?date .
                
            }        
        }
       
        """
        )
        df_cultural_heritage_objects = get(endpoint, query, True)
        return df_cultural_heritage_objects

    # it returns a data frame with all the authors of the cultural heritage object identified by the input id.
    def getAuthorsOfCulturalHeritageObject(self, objectId: str) -> DataFrame:
        endpoint = self.getDbPathOrUrl() + "sparql"
        query = (
            self.query_header
            + """
        SELECT ?uri ?author_name ?id
        WHERE {
            ?obj schema:identifier "%s" .
            ?obj schema:author ?uri .
            ?uri schema:name ?author_name .
          	?uri schema:identifier ?id .
        }
        """
            % objectId
        )
        df_authors_of_cultural_heritage_objects = get(endpoint, query, True)
        return df_authors_of_cultural_heritage_objects

    # it returns a data frame with all the cultural heritage objects authored by the person identified by the input id.
    def getCulturalHeritageObjectsAuthoredBy(self, personId: str) -> DataFrame:
        endpoint = self.getDbPathOrUrl() + "sparql"
        query = (
            self.query_header
            + """
        SELECT ?uri ?type ?id ?title ?date ?owner ?place
        WHERE {
            ?uri schema:author ?author .
            ?author schema:identifier "%s" .
            ?uri rdf:type ?type .
            ?uri schema:identifier ?id .
            ?uri schema:title ?title .
            ?uri schema:dateCreated ?date .
            ?uri github:owner ?owner .
            ?uri schema:itemLocation ?place .
        }
        """
            % personId
        )
        df_cultural_heritage_objects_authored_by = get(endpoint, query, True)
        return df_cultural_heritage_objects_authored_by


# Process from the JSON Handler
class ProcessDataQueryHandler(QueryHandler):  # Ludovica
    all_cols_null_tech = "internalId, responsibleInstitute, responsiblePerson, NULL AS technique, tool, startDate, endDate, objectId"

    # returns a dataframe with all the activities in the database.
    def getAllActivities(self) -> DataFrame:
        with connect(self.getDbPathOrUrl()) as con:
            query_all_activities = f"""
            SELECT *
            FROM Acquisition
            UNION
            SELECT {self.all_cols_null_tech} 
            FROM Processing
            UNION
            SELECT {self.all_cols_null_tech} 
            FROM Exporting
            UNION
            SELECT {self.all_cols_null_tech} 
            FROM Modelling
            UNION
            SELECT {self.all_cols_null_tech}  
            FROM Optimising
            ORDER BY acquisition.objectId;
            """

            df_all_activities = read_sql(query_all_activities, con)

        return df_all_activities

    # returns a data frame with all the activities that have, as responsible institution, any that matches (even partially) with the input string.
    def getActivitiesByResponsibleInstitution(self, partialName: str) -> DataFrame:
        with connect(self.getDbPathOrUrl()) as con:
            query = f"""
                SELECT * 
                FROM (
                    SELECT *
                    FROM Acquisition
                    UNION
                    SELECT {self.all_cols_null_tech}
                    FROM Exporting
                    UNION
                    SELECT {self.all_cols_null_tech}
                    FROM Modelling
                    UNION
                    SELECT {self.all_cols_null_tech}
                    FROM Optimising
                    UNION
                    SELECT {self.all_cols_null_tech}
                    FROM Processing
                ) AS subquery
                WHERE responsibleInstitute LIKE '%{partialName}%'
                ORDER BY objectId;
                """
            df = read_sql(query, con)
        return df

    #  returns a data frame with all the activities that have, as responsible person, any that matches (even partially) with the input string.
    def getActivitiesByResponsiblePerson(self, partialName: str) -> DataFrame:
        with connect(self.getDbPathOrUrl()) as con:
            query = f"""
            SELECT * 
            FROM (
                SELECT *
                FROM Acquisition
                UNION
                SELECT {self.all_cols_null_tech} 
                FROM Exporting
                UNION
                SELECT  {self.all_cols_null_tech} 
                FROM Modelling
                UNION
                SELECT {self.all_cols_null_tech} 
                FROM Optimising
                UNION
                SELECT {self.all_cols_null_tech} 
                FROM Processing
            ) AS subquery
            WHERE responsiblePerson LIKE '%{partialName}%'
            ORDER BY objectId;
            """

            df = read_sql(query, con)
        return df

    # returns a data frame with all the activities that have, as a tool used, any that matches (even partially) with the input string.
    def getActivitiesUsingTool(self, partialName: str) -> DataFrame:
        with connect(self.getDbPathOrUrl()) as con:
            query = f"""
            SELECT * 
            FROM (
                SELECT *
                FROM Acquisition
                UNION
                SELECT {self.all_cols_null_tech} 
                FROM Exporting
                UNION
                SELECT {self.all_cols_null_tech}  
                FROM Modelling
                UNION
                SELECT {self.all_cols_null_tech} 
                FROM Optimising
                UNION
                SELECT {self.all_cols_null_tech} 
                FROM Processing
            ) AS subquery
            WHERE tool LIKE '%{partialName}%'
            ORDER BY objectId;
            """

            df = read_sql(query, con)
        return df

    # returns a data frame with all the activities that started either exactly on or after the date specified as input.
    def getActivitiesStartedAfter(self, date: str) -> DataFrame:
        with connect(self.getDbPathOrUrl()) as con:
            query = f"""
                SELECT * 
                FROM (
                SELECT *
                FROM Acquisition
                UNION
                SELECT {self.all_cols_null_tech} 
                FROM Exporting
                UNION
                SELECT {self.all_cols_null_tech} 
                FROM Modelling
                UNION
                SELECT {self.all_cols_null_tech} 
                FROM Optimising
                UNION
                SELECT {self.all_cols_null_tech} 
                FROM Processing
            ) AS subquery
            WHERE startDate >= "{date}"
            ORDER BY objectId;
            """

            df = read_sql(query, con)
        return df

    # returns a data frame with all the activities that ended either exactly on or before the date specified as input.
    def getActivitiesEndedBefore(self, date: str) -> DataFrame:
        with connect(self.getDbPathOrUrl()) as con:
            query = f"""
            SELECT 
            * FROM (
                SELECT *
                FROM Acquisition
                UNION
                SELECT {self.all_cols_null_tech} 
                FROM Exporting
                UNION
                SELECT {self.all_cols_null_tech}  
                FROM Modelling
                UNION
                SELECT {self.all_cols_null_tech} 
                FROM Optimising
                UNION
                SELECT {self.all_cols_null_tech} 
                FROM Processing
            ) AS subquery
            WHERE endDate <= "{date}"
            ORDER BY objectId;
            """

            df = read_sql(query, con)
        return df

    # returns a data frame with all the acquisitions that have, as a technique used, any that matches (even partially) with the input string.
    def getAcquisitionsByTechnique(self, partialName: str) -> DataFrame:
        with connect(self.getDbPathOrUrl()) as con:
            query = f"""
            SELECT *
            FROM Acquisition
            WHERE technique LIKE "%{partialName}%"
            ORDER BY objectId
            """

            df = read_sql(query, con)
        return df
