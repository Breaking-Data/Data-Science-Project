from json import load
from pprint import pprint
from pandas import DataFrame, concat
from sqlite3 import connect

class Handler:
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

            with connect(rel_path) as con:
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