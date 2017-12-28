#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os

import pandas as pd

from pfc_utils.plant_image_processing import PlantImageProc

if __name__ == '__main__':
    data_folder = sys.argv[1]
    image_proc = PlantImageProc()
    output = pd.DataFrame()
    for f in os.listdir(data_folder):
        filepath = os.path.join(data_folder, f)
        shape_data_dict = image_proc.get_plant_data(filepath)
        shape_data_dict = pd.Series(shape_data_dict, name=f)
        output = output.append(shape_data_dict)

    output.to_csv('result.csv')
        