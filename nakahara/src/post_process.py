#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import numpy as np
import pandas as pd

from pfc_utils.data_manipulator import DataManipulator

RECIPE_START = 'recipe_start'
RECIPE_END = 'recipe_end'

server_address = 'http://foodcomputer.akg.t.u-tokyo.ac.jp'
port = 5984
db_name = 'environmental_data_point'
view_id = 'openag/all_vars'


pfc_db = DataManipulator(server_address=server_address, port=port, db_name=db_name, view_id=view_id)
recipe_history_master = pfc_db.get_recipe_history(pfc_id=1)


def get_temp_recipe(ser):
    t = ser.timestamp
    last_recipe = recipe_history_master[
        ~(recipe_history_master.index > t)
    ].iloc[-1]
    return last_recipe.recipe_start


def get_plant_id(ser):
    t = pd.Timestamp(ser.timestamp)
    plant_id_master = {
        1: {'from': pd.Timestamp('20171115'), 'to': pd.Timestamp('20171129')},
        2: {'from': pd.Timestamp('20171203'), 'to': pd.Timestamp('20171228')},
        3: {'from': pd.Timestamp('20171229'), 'to': pd.Timestamp('20180131')}
    }

    for plant_id_candidate, cond in plant_id_master.items():
        if t > cond['from'] and t < cond['to']:
            plant_id = plant_id_candidate
            return plant_id

    return np.nan


def growth_rate(df, periods=10):
    time_span = pd.to_datetime(df.timestamp).diff(periods=periods).astype('timedelta64[s]').dropna()
    diffed = df.loc[:, ['bottom', 'left', 'right', 'top']].diff(periods=periods).dropna()
    return diffed.divide(time_span, axis='rows').assign(
        time_span = time_span
    ).set_index(pd.to_datetime(df.timestamp.iloc[periods:]))


if __name__ == '__main__':
    _, leafarea_filepath = sys.argv[:2]
    leafarea_master = pd.read_csv(leafarea_filepath, index_col=0)

    # add recipe
    leafarea_master['recipe'] = leafarea_master.apply(get_temp_recipe, axis=1)
    leafarea_master.set_index('timestamp').to_csv(os.path.join(
        os.path.dirname(leafarea_filepath),
        os.path.splitext(os.path.basename(leafarea_filepath))[0] + '_withrecipe.csv'
    ))

    # add plant id
    leafarea_master = leafarea_master.replace(
        -1, np.nan
    ).dropna(
        thresh=2
    ).assign(
        plant_id = leafarea_master.apply(get_plant_id, axis=1)
    ).dropna()
    df_growthrate = leafarea_master.groupby('plant_id').apply(growth_rate, periods=10)
    df_growthrate.to_csv(os.path.join(
        os.path.dirname(leafarea_filepath),
        os.path.splitext(os.path.basename(leafarea_filepath))[0] + '_growthrate.csv'
    ))