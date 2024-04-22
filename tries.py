from pandas import DataFrame, read_sql
from handler import *
from sqlite3 import connect
import pandas as pd
from mashup import BasicMashup
from cultural_objects import *

process_qh = ProcessDataQueryHandler()
process_qh.setDbPathOrUrl("relational.db")

metadata_qh = MetadataQueryHandler()
metadata_qh.setDbPathOrUrl("http://192.168.1.197:9999/blazegraph/")


mashup = BasicMashup()
mashup.addMetadataHandler(metadata_qh)
mashup.addProcessHandler(process_qh)

print(mashup.getAllCulturalHeritageObjects()[1])
