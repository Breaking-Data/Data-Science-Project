from json import load
from pprint import pprint
from pandas import DataFrame, concat
from sqlite3 import connect
from pandas import read_csv, Series
from rdflib import Graph, URIRef, Namespace, RDF, Literal
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore


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

    def pushDataToDb(self, json_file):
        
        with open(json_file) as f:
            list_of_dict = load(f)
            keys = list_of_dict[0].keys()
            # a dataframe representing the entire json file
            j_df = DataFrame(list_of_dict, columns=keys)
             
            table_dict = {}
            for column_name in j_df.columns.to_list()[1:]:
                cell = j_df.loc[0,column_name]
                if type(cell) == dict:
                    keys = cell.keys() 
                    table_dict[column_name] = DataFrame(columns=keys)
                    # creates new column with the unic id for each table
                    table_dict[column_name].insert(0, f"{column_name}"+" id", [])
                # works but not final and not usefull
                #if type(cell) == str:
                #  table_dict[column_name] = DataFrame([],columns=[column_name,"acquisition id","processing id","modelling id","optimising id","exporting id"])
        
            for table_name, table in table_dict.items():
                for column_to_fill in table.columns.to_list()[1:]:
                    
                    unic_identifiers = []
                    content = []
                    num_rows = len(j_df)
                    i = 0
                    id_counter = 1

                    while i < num_rows:

                        cell = j_df.loc[i][table_name]
                        column_value = cell[column_to_fill]
                        if type(column_value) == list:
                            column_value = ", ".join(column_value) #list or string?
                        if column_value == "":
                            column_value = None
                        content.append(column_value)
                        # could be erased when we understand  foreign keys
                        unic_identifiers.append(f"{table.columns[0]} {id_counter}") 
                        i += 1
                        id_counter += 1

                    table[column_to_fill] = content
                    table[table.columns[0]] = unic_identifiers
                    # the object id row can be removed if not needed (just delite this line) 
                    table["object id"] = j_df[j_df.columns[0]]

            with connect(self.dbPathOrUrl) as con:
                for table_name, table in table_dict.items():
                    data_type_dict = {}
                    for column in table.columns.to_list():
                        if table[column].dtype == int:
                                data_type_dict[f"{column}"] = "integer"
                        if table[column].dtype== str:
                                data_type_dict[f"{column}"] = "string"

                        table.to_sql(f"{table_name}", con, if_exists="replace",index=False,
                                            dtype = data_type_dict)
                        
            con.close() # I don't know if we need it 

        if type(json_file) == str:
            return True
        else:
            False

# exemplar execution
rel_path = "relational.db"
process = ProcessDataUploadHandler()
process.setDbPathOrUrl(rel_path)
process.pushDataToDb("data/process.json")

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
        name = URIRef(schema.name) # I'm not sure about this, 'cause "name" it's a propriety of the superclass "Thing" in schema.org
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
        metadata_frame = read_csv(path, keep_default_na=False, dtype={"Id": "string",
                                                                       "Type": "string", 
                                                                       "Title": "string", 
                                                                       "Date": "string", 
                                                                       "Author": "string", 
                                                                       "Owner": "string",
                                                                       "Place": "string"})
        
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
                person_id = author[(indx_for_split+1):-1]
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

        endpoint = self.dbPathOrUrl

        store.open((endpoint, endpoint))

        for triple in metadata_graph.triples((None, None, None)):
                store.add(triple)

        store.close()

        return True