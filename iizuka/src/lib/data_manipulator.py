import couchdb
import datetime
import pandas as pd
import numpy as np

RECIPE_START = 'recipe_start'
RECIPE_END = 'recipe_end'
pfc1_address = 'http://foodcomputer.akg.t.u-tokyo.ac.jp'
pfc2_address = 'http://foodcomputer2.akg.t.u-tokyo.ac.jp'
PFC_ADRESS_LIST = [pfc1_address, pfc2_address]
ENVIRONMENTAL_DATA_POINT = 'environmental_data_point'
RECIPE_PORT = 5984
RECIPE_VIEW_ID = 'openag/recipe_vars'

def to_datetime(unixTime):
    return datetime.datetime.fromtimestamp(
        unixTime
    )

class DataManipulator():
    def __init__(self, server_address='http://localhost', port=5984,
        db_name='environmental_data_point', view_id='pfc/all_vars'):
        self.server_address = server_address
        self.port = port
        self.db_name = db_name
        self.server = couchdb.Server('{}:{}/'.format(server_address, port))
        self.db = self.server[self.db_name]
        self.view_id = view_id

    def init_recipe_server(self, pfc_id=1):
        if  pfc_id > len(PFC_ADRESS_LIST) + 1 or pfc_id < 1:
            print('invalid pfc_id')
            return None
        self.recipe_server = couchdb.Server('{}:{}/'.format(PFC_ADRESS_LIST[pfc_id - 1], RECIPE_PORT))
        self.recipe_db = self.recipe_server[ENVIRONMENTAL_DATA_POINT]
        self.recipe_view_id = RECIPE_VIEW_ID
        self.pfc_id = pfc_id

    def check_condition(self, item=None, condition_dict=None):
        if condition_dict is None:
            return True
        for key in condition_dict:
            if item.value[key] != condition_dict[key]:
                return False
        return True

    def get_observed_data(self, variable, environment='environment_1'):
        condition_dict = {'variable': variable, 'environment': environment, 'is_desired':False}
        return self.get_variable_data(condition_dict)

    def get_target_data(self, variable, environment='environment_1'):
        condition_dict = {'variable': variable, 'environment': environment, 'is_desired':True}
        return self.get_variable_data(condition_dict)

    def get_recipe_history(self, pfc_id=1):
        '''
        input:
            pfc_id: 1 or 2 can be, 2 represents pfc2
        return:
            recipe_start
        '''
        if not hasattr(self, 'recipe_db'):
            self.init_recipe_server(pfc_id=pfc_id)
        condition_dict_start = {'variable': RECIPE_START, 'is_desired':True}
        print(self.recipe_db, condition_dict_start, RECIPE_VIEW_ID)
        recipe_start_list = self.get_series_data(
            db=self.recipe_db, condition_dict=condition_dict_start, view_id=RECIPE_VIEW_ID
        )
        ts_recipe_start = pd.Series(
            recipe_start_list[:,0].astype(dtype=np.str), index=recipe_start_list[:,1]
        )

        condition_dict_end = {'variable': RECIPE_END, 'is_desired':True}
        recipe_end_list = self.get_series_data(
            db=self.recipe_db, condition_dict=condition_dict_end, view_id=RECIPE_VIEW_ID
        )
        ts_recipe_end = pd.Series(
            recipe_end_list[:,0].astype(dtype=np.str), index=recipe_end_list[:,1]
        )
        return pd.DataFram({RECIPE_START:ts_recipe_start, RECIPE_END:ts_recipe_end})

    def get_variable_data(self, condition_dict):
        '''
        input :
            condition_dict <-
                {key : value,,,}
                key means which attribute in doc should be refered
                value means what designated attribute should be
        return :
            series data
        '''
        date_value_list = self.get_series_data(db=self.db, condition_dict=condition_dict, view_id=self.view_id)
        return pd.Series(date_value_list[:,0].astype(dtype=np.float64), index=date_value_list[:,1])


    def get_series_data(self, db, condition_dict, view_id):
        '''
        return date_value_lsit
            date_value_lsit[:, 0] is a list of values
            date_value_lsit[:, 1] is a list of unixtime stamp
        '''
        variable_data_list = []
        unique_time_set = set([])
        for item in self.db.view(view_id):
            if self.check_condition(item, condition_dict):
                if not item.value['timestamp'] in unique_time_set:
                    variable_data_list.append(item.value)
                    unique_time_set.add(item.value['timestamp'] )
        if len(variable_data_list) ==0:
            return None

        date_value_list = np.array([[
            variable_data['value'], to_datetime(variable_data['timestamp'])]
            for variable_data in variable_data_list])
        return date_value_list

