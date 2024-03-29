from json import load
from pprint import pprint
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

        # create a big datafame representing the entire json file.
        with open(json_file) as f:
            list_of_dict = load(f)
            keys = list_of_dict[0].keys()
            j_df = DataFrame(list_of_dict, columns=keys)

            # create empty dataframes (with the correct column names) for each activity.
            df_dict = {}
            for column_name in j_df.columns.to_list()[1:]:
                cell = j_df.loc[0, column_name]

                if type(cell) == dict:
                    keys = cell.keys()
                    df_dict[column_name] = DataFrame(columns=keys)
                    df_dict[column_name].insert(0, "internal Id", [])

            # populate each empty dataframe with the correct information from j_df
            for df_name, df in df_dict.items():

                for column_to_fill in df.columns.to_list()[1:]:
                    unic_identifiers = []
                    content = []
                    num_rows = len(j_df)
                    i = 0
                    id_counter = 1

                    while i < num_rows:
                        cell = j_df.loc[i][df_name]
                        column_value = cell[column_to_fill]
                        if type(column_value) == list:
                            column_value = ", ".join(column_value)
                        if column_value == "":
                            column_value = None
                        content.append(column_value)
                        unic_identifiers.append(f"{df_name}-{id_counter}")
                        i += 1
                        id_counter += 1

                    df[column_to_fill] = content
                    df[df.columns[0]] = unic_identifiers
                    df["object id"] = j_df[j_df.columns[0]]

            # correct the tables and the columns names
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

            # storing the tables into the relational database
            with connect(self.dbPathOrUrl) as con:
                for table_name, table in table_dict.items():
                    data_type_dict = {}

                    for column in table.columns.to_list():
                        data_type_dict[f"{column}"] = "string"
                        con.execute(f"DROP TABLE IF EXISTS {table_name}")
                        table.to_sql(
                            f"{table_name}",
                            con,
                            if_exists="replace",
                            index=False,
                            dtype=data_type_dict,
                        )

        # check if all the tables are correctly stored into the relational db           
        cursor = con.cursor()          
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        c = cursor.fetchall()
        tables_in_db = []
        for table in c:
            tables_in_db.append(table[0])
        tables_in_dict = table_dict.keys()
        if set(tables_in_dict) == set(tables_in_db):
            return True
        else:
            return False


# The class for uploading the csv file to a graph database
class MetadataUploadHandler(UploadHandler):
    def pushDataToDb(self, path):

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
        name = URIRef(
            schema.name
        )  # I'm not sure about this, 'cause "name" it's a propriety of the superclass "Thing" in schema.org
        # (I'll explain to you my doubts)

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

        # the process to push the data
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

        # populating the graph with all the people
        people_authority_ids = dict()
        people_object_ids = dict()
        for idx, row in metadata_frame.iterrows():
            author = row["Author"]
            if author != "":

                # Here I'm isolating the authority identifier and the name of the author
                for i, c in enumerate(author):
                    if c == "(":
                        indx_for_split = i

                person_name = author[:indx_for_split]
                person_id = author[(indx_for_split + 1) : -1]
                object_id = row["Id"]

                if person_id in people_authority_ids.keys():
                    person_uri = people_authority_ids[person_id]
                    people_object_ids[object_id] = person_uri

                else:

                    local_id = "person-" + str(idx)
                    subj = URIRef(base_url + local_id)

                    # adding to the graph the type person, the identifier and the name of the person
                    metadata_graph.add((subj, RDF.type, Person))
                    metadata_graph.add((subj, identifier, Literal(person_id)))
                    metadata_graph.add((subj, name, Literal(person_name)))

                    people_authority_ids[person_id] = subj
                    people_object_ids[object_id] = subj

        # populating the graph with all the cultural heritage objects
        for idx, row in metadata_frame.iterrows():
            local_id = "culturalobject-" + str(idx)
            subj = URIRef(base_url + local_id)

            if row["Type"] != "":
                if row["Type"] == "Nautical chart":
                    metadata_graph.add((subj, RDF.type, NauticalChart))

                elif row["Type"] == "Manuscript Plate":
                    metadata_graph.add((subj, RDF.type, ManuscriptPlate))

                elif row["Type"] == "Manuscript Volume":
                    metadata_graph.add((subj, RDF.type, ManuscriptVolume))

                elif row["Type"] == "Printed Volume":
                    metadata_graph.add((subj, RDF.type, PrintedVolume))

                elif row["Type"] == "Printed Material":
                    metadata_graph.add((subj, RDF.type, PrintedMaterial))

                elif row["Type"] == "Herbarium":
                    metadata_graph.add((subj, RDF.type, Herbarium))

                elif row["Type"] == "Specimen":
                    metadata_graph.add((subj, RDF.type, Specimen))

                elif row["Type"] == "Painting":
                    metadata_graph.add((subj, RDF.type, Painting))

                elif row["Type"] == "Model":
                    metadata_graph.add((subj, RDF.type, Model))

                else:
                    metadata_graph.add((subj, RDF.type, Map))

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
                metadata_graph.add((subj, hasAuthor, people_object_ids[row["Id"]]))

        # sending the graph to the database
        store = SPARQLUpdateStore()

        endpoint = self.dbPathOrUrl + "sparql"

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
        df_sparql = get(endpoint, query, True)

        n_triples_in_graph = len(metadata_graph)
        n_triples_in_database = 0
        for idx, row in df_sparql.iterrows():
            n_triples_in_database += 1

        return n_triples_in_database == n_triples_in_graph


class QueryHandler(Handler):
    def getById(self, id: str) -> DataFrame:
        # !COMPLETE THE RELETAIONAL DB QUERY!
        db_address = self.getDbPathOrUrl()
        if ".db" in db_address:
            with connect(db_address) as con:
                query = (
                    """
                SELECT *
                FROM
                """
                    % id
                )
                df_entity = read_sql(query, con)

        else:
            endpoint = db_address + "sparql"
            query = (
                """
            PREFIX schema: <http://schema.org/>

            SELECT ?entity
            WHERE {
                ?entity schema:identifier "%s" .
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

    """

    # it returns a data frame containing all the people included in the database.
    def getAllPeople(self) -> DataFrame:
        endpoint = self.getDbPathOrUrl() + "sparql"
        query = (
            self.query_header
            + """
        SELECT ?person
        WHERE {
            ?person rdf:type schema:Person .
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
        SELECT ?cultural_heritage_objects
        WHERE {
            ?cultural_heritage_objects rdf:type ?o .
            FILTER (?o != schema:Person)
        }
        """
        )
        df_cultural_heritage_objects = get(endpoint, query, True)
        return df_cultural_heritage_objects

    # it returns a data frame with all the authors of the cultural heritage objects identified by the input id.
    def getAuthorsOfCulturalHeritageObject(self, objectId: str) -> DataFrame:
        endpoint = self.getDbPathOrUrl() + "sparql"
        query = (
            self.query_header
            + """
        SELECT ?authors
        WHERE {
            "%s" schema:author ?authors .
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
        SELECT ?cultural_object
        WHERE {
            ?cultural_object schema:author "%s" .
        }
        """
            % personId
        )
        df_cultural_heritage_objects_authored_by = get(endpoint, query, True)
        return df_cultural_heritage_objects_authored_by


# JSON Handler
class ProcessDataQueryHandler(QueryHandler):
    def getAllActivities(self) -> DataFrame:
        with connect(self.getDbPathOrUrl()) as con:
            query_all_activities = """
            SELECT internalId, responsibleInstitute, responsiblePerson, tool, startDate, endDate, objectId, technique 
            FROM Acquisition
            UNION
            SELECT internalId, responsibleInstitute, responsiblePerson, tool, startDate, endDate, objectId, NULL AS technique 
            FROM Exporting
            UNION
            SELECT internalId, responsibleInstitute, responsiblePerson, tool, startDate, endDate, objectId, NULL AS technique 
            FROM Modelling
            UNION
            SELECT internalId, responsibleInstitute, responsiblePerson, tool, startDate, endDate, objectId, NULL AS technique 
            FROM Optimising
            ORDER BY acquisition.objectId;
            """

            df_all_activities = read_sql(query_all_activities, con)

        return df_all_activities

    # add all the other columns for queries???
    def getActivitiesByResponsibleInstitution(self, partialName: str) -> DataFrame:
        with connect(self.getDbPathOrUrl()) as con:
            query = f"""
            SELECT * 
            FROM (SELECT internalId, objectId, responsibleInstitute 
            FROM Acquisition
            UNION
            SELECT internalId, objectId, responsibleInstitute 
            FROM Exporting
            UNION
            SELECT  internalId, objectId, responsibleInstitute 
            FROM Modelling
            UNION
            SELECT internalId, objectId, responsibleInstitute 
            FROM Optimising
            UNION
            SELECT internalId, objectId, responsibleInstitute 
            FROM Processing) AS subquery
            WHERE responsibleInstitute LIKE '%{partialName}%'
            ORDER BY objectId;"""

            df = read_sql(query, con)
        return df

    # add all the other columns for queries???
    def getActivitiesByresponsiblePerson(self, partialName: str) -> DataFrame:
        with connect(self.getDbPathOrUrl()) as con:
            query = f"""SELECT * FROM 
            (SELECT internalId, objectId, responsiblePerson
            FROM Acquisition
            UNION
            SELECT internalId, objectId, responsiblePerson 
            FROM Exporting
            UNION
            SELECT  internalId, objectId, responsiblePerson 
            FROM Modelling
            UNION
            SELECT internalId, objectId, responsiblePerson 
            FROM Optimising
            UNION
            SELECT internalId, objectId, responsiblePerson 
            FROM Processing) AS subquery
            WHERE responsiblePerson LIKE '%{partialName}%'
            ORDER BY objectId;"""

            df = read_sql(query, con)
        return df

    # add all the other columns for queries???
    def getActivitiesUsingTool(self, partialName: str) -> DataFrame:
        with connect(self.getDbPathOrUrl()) as con:
            query = f"""SELECT * FROM (SELECT internalId, objectId, tool
            FROM Acquisition
            UNION
            SELECT internalId, objectId, tool 
            FROM Exporting
            UNION
            SELECT  internalId, objectId, tool 
            FROM Modelling
            UNION
            SELECT internalId, objectId, tool 
            FROM Optimising
            UNION
            SELECT internalId, objectId, tool 
            FROM Processing) AS subquery
            WHERE tool LIKE '%{partialName}%'
            ORDER BY objectId;"""

            df = read_sql(query, con)
        return df

    def getActivitiesUsingTool(self, partialName: str) -> DataFrame:
        with connect(self.getDbPathOrUrl()) as con:
            query = f"""SELECT * FROM (SELECT internalId, objectId, tool
            FROM Acquisition
            UNION
            SELECT internalId, objectId, tool 
            FROM Exporting
            UNION
            SELECT  internalId, objectId, tool 
            FROM Modelling
            UNION
            SELECT internalId, objectId, tool 
            FROM Optimising
            UNION
            SELECT internalId, objectId, tool 
            FROM Processing) AS subquery
            WHERE tool LIKE '%{partialName}%'
            ORDER BY objectId;"""

            df = read_sql(query, con)
        return df

    def getActivitiesStartedAfter(self, date: str) -> DataFrame:
        with connect(self.getDbPathOrUrl()) as con:
            query = f"""
            SELECT * FROM (SELECT internalId, objectId, startDate
            FROM Acquisition
            UNION
            SELECT internalId, objectId, startDate 
            FROM Exporting
            UNION
            SELECT  internalId, objectId, startDate
            FROM Modelling
            UNION
            SELECT internalId, objectId, startDate
            FROM Optimising
            UNION
            SELECT internalId, objectId, startDate
            FROM Processing) AS subquery
            WHERE startDate >= "{date}"
            ORDER BY objectId;"""

            df = read_sql(query, con)
        return df

    def getActivitiesEndedBefore(self, date: str) -> DataFrame:
        with connect(self.getDbPathOrUrl()) as con:
            query = f"""
            SELECT * FROM (SELECT internalId, objectId, endDate
            FROM Acquisition
            UNION
            SELECT internalId, objectId, endDate 
            FROM Exporting
            UNION
            SELECT  internalId, objectId, endDate 
            FROM Modelling
            UNION
            SELECT internalId, objectId, endDate 
            FROM Optimising
            UNION
            SELECT internalId, objectId, endDate 
            FROM Processing) AS subquery
            WHERE endDate <= "{date}"
            ORDER BY objectId;"""

            df = read_sql(query, con)
        return df

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
