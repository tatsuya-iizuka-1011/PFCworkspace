#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
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


if __name__ == '__main__':
    _, leafarea_filepath = sys.argv[:2]
    leafarea_master = pd.read_csv(leafarea_filepath, index_col=0)
    leafarea_master['recipe'] = leafarea_master.apply(get_temp_recipe, axis=1)
    leafarea_master.set_index('timestamp').to_csv(os.path.join(
        os.path.dirname(leafarea_filepath),
        os.path.splitext(os.path.basename(leafarea_filepath))[0] + '_withrecipe.csv'
    ))