from pandas import DataFrame, read_sql
from handler import *
from sqlite3 import connect
import pandas as pd
from mashup import BasicMashup
from cultural_objects import *


metadata_qh = MetadataQueryHandler()
metadata_qh.setDbPathOrUrl("http://10.201.16.211:9999/blazegraph/")


mashup = BasicMashup()
mashup.addMetadataHandler(metadata_qh)

print(mashup.getAllCulturalHeritageObjects()[3].getAuthors())
