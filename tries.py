from pandas import DataFrame, read_sql
from handler import *
from sqlite3 import connect
import pandas as pd
from mashup import BasicMashup
from cultural_objects import *


metadata_qh = MetadataQueryHandler()
metadata_qh.setDbPathOrUrl("")

process_qh = ProcessDataQueryHandler()
process_qh.setDbPathOrUrl("relational.db")


mashup = BasicMashup()
mashup.addMetadataHandler(metadata_qh)
mashup.addProcessHandler(process_qh)

