import couchdb
import datetime
import matplotlib.pyplot as plt
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import time

server_address = 'http://localhost'
port = 5984
db_name = 'environmental_data_point'

server = couchdb.Server('{}:{}/'.format(server_address, port))
env_db = server[db_name]

variable_view =  env_db.view('pfc/all_vars')
print(len(variable_view))
