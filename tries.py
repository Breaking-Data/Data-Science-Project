from pandas import DataFrame, read_sql
from handler import *
from sqlite3 import connect
import pandas as pd
from mashup import BasicMashup
from cultural_objects import *



metadata_uh = MetadataUploadHandler()
metadata_uh.setDbPathOrUrl("http://192.168.1.20:9999/blazegraph/")
print(metadata_uh.pushDataToDb("Data-Science-Project\data\meta.csv"))
metadata_qh = MetadataQueryHandler()
metadata_qh.setDbPathOrUrl("http://192.168.1.20:9999/blazegraph/")


mashup = BasicMashup()
mashup.addMetadataHandler(metadata_qh)

id = "VIAF:2465365"
my_object = BasicMashup.getEntityById(id)
print(my_object.getName())
