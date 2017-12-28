import couchdb
import datetime
import matplotlib.pyplot as plt
from pandas import Series, DataFrame
import pandas as pd
import numpy as np

#plt.style.use('dark_background')
#plt.style.use('ggplot')

server_address = 'http://localhost'
port = 5984
db_name = 'environmental_data_point'

server = couchdb.Server('{}:{}/'.format(server_address, port))
env_db = server[db_name]

def to_datetime(unixTime):
    return datetime.datetime.fromtimestamp(
        unixTime
    )

class DataManipulator():
    def __init__(self, server_address='http://localhost', port=5984, db_name='environmental_data_point'):
        self.server_address = server_address
        self.port = port
        self.db_name = db_name
        self.server = couchdb.Server('{}:{}/'.format(server_address, port))
        self.db = self.server[self.db_name]

    def check_condition(self, item=None, condition_dict=None):
        if condition_dict is None:
            return True
        for key in condition_dict:
            if item.value[key] != condition_dict[key]:
                return False
        return True

    def get_observed_data(self, variable, environment='environment_1'):
        condition_dict = {'variable': variable, 'environment': environment, 'is_desired':False}
        return self.get_series_data(condition_dict)

    def get_target_data(self, variable, environment='environment_1'):
        condition_dict = {'variable': variable, 'environment': environment, 'is_desired':True}
        return self.get_series_data(condition_dict)

    def get_series_data(self, condition_dict):
        variable_data_list = []
        unique_time_set = set([])
        for item in env_db.view('pfc/all_vars'):
            if self.check_condition(item, condition_dict):
                if not item.value['timestamp'] in unique_time_set:
                    variable_data_list.append(item.value)
                    unique_time_set.add(item.value['timestamp'] )
        if len(variable_data_list) ==0:
            return None

        date_value_list = np.array([[
            variable_data['value'], to_datetime(variable_data['timestamp'])]
            for variable_data in variable_data_list])
        ts = Series(date_value_list[:,0].astype(dtype=np.float64), index=date_value_list[:,1])
        return ts
