import couchdb
import datetime
import matplotlib.pyplot as plt
from pandas import Series, DataFrame
import pandas as pd
import numpy as np

class DatabaseManipulator(object):
    def __init__(self, server, port, db_name):
        server = couchdb.Server('{}:{}/'.format(server, port))
        db = server[db_name]
        self.db = db
        self.ts_dict = {}
        plt.style.use('dark_background')

    def convertToDateTimeObj(self, unixTime):
        return datetime.datetime.fromtimestamp(
            unixTime
        )

    def showVaribableGraph(self, variable, x_range=None, y_range=None):
        if variable in self.ts_dict:
            self.ts_dict[variable].plot()
            plt.title(variable)
            plt.show()
        else:
            print(' is not loaded'.format(variable))

    def showEachVaribableGraph(self, variable, x_range=None, y_range=None):
        #draw  date value graph  for each variable
        for variable, date_value in self.ts_dict.iteritems():
            self.showVaribableGraph(variable, date_value)
        return


import couchdb
import datetime
import matplotlib.pyplot as plt
from pandas import Series, DataFrame
import pandas as pd
import numpy as np

class DatabaseManipulator(object):
    def __init__(self, server, port, db_name):
        server = couchdb.Server('{}:{}/'.format(server, port))
        db = server[db_name]
        self.db = db
        self.ts_dict = {}
        plt.style.use('dark_background')

    def convertToDateTimeObj(self, unixTime):
        return datetime.datetime.fromtimestamp(
            unixTime
        )


class EnvironmentalDatabaseManipulator(DatabaseManipulator):
    def __init__(self, server, port, db_name):
        super(EnvironmentalDatabaseManipulator, self).__init__( server, port, db_name)

    def getSensorDataList(self, variable, limit=1000):
        '''
        argments are
        variable : envrionemental name such as 'air_humidity'  as a string
        limit : number of data points to load from database

        return object of Series
        index is time labeled, value list (1d ndarray) represents sensor data points.
        '''
        map_fun = '''function(doc) {{
            if (doc.variable == '{}')
                emit(doc.timestamp, doc.value);
        }}'''.format(variable)

        row_list = self.db.query(map_fun, descending=True, limit=limit)
        date_value_list = np.array([[
            row.value,
            self.convertToDateTimeObj(row.key)]
        for row in row_list])
        ts = Series(date_value_list[:,0].astype(dtype=np.float64), index=date_value_list[:,1])
        return ts

    def setSensorDataList(self, variable, limit=1000):
        self.ts_dict[variable] = self.getSensorDataList(variable, limit)
        return

    def plotVariableGraph(self, variable, ylim=(0,5) ):
        if variable in self.ts_dict:
            ts = self.ts_dict[variable]
            ts_tmp = ts[::2] #since there are the same data duplicated
            tmp_df = DataFrame(ts_tmp)
            tmp_df.plot(ylim=ylim, style='o', figsize=(15,10))
            plt.title(variable)
            plt.show()
        else:
            print('{} does not exist in ts_dict'.format(variable))


class ActuatorDatabaseManipulator(DatabaseManipulator):
    def __init__(self, server, port, db_name):
        super(ActuatorDatabaseManipulator, self).__init__( server, port, db_name)

    def getActuatorDataList(self, variable, limit=1000):
        map_fun = '''function(doc) {{
            if (doc.variable == '{}')
                emit(doc.timestamp, doc.value);
        }}'''.format(variable)
        row_list = self.db.query(map_fun, descending=True, limit=limit)
        date_value_list = np.array([[
            self.convertToFloat(row.value),
            self.convertToDateTimeObj(row.key)]
        for row in row_list])
        ts = Series(date_value_list[:,0].astype(dtype=np.float64), index=date_value_list[:,1])
        return ts

    def convertToFloat(self, uni_s):
        s = uni_s.encode('utf-8')
        try:
            return float(s)
        except ValueError:
            if s.lower() == 'true':
                return 1
            else:
                return 0.0

    def setActuatorDataList(self, variable, limit=1000):
        self.ts_dict[variable] = self.getActuatorDataList(variable, limit)
        return
