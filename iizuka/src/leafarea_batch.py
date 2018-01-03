#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import sys
import os

from tqdm import tqdm
import pandas as pd

from pfc_utils.plant_image_processing import PlantImageProc

positions = ('top', 'left', 'right', 'bottom')


def get_contour_area(ser):
        areas = []
        for attr in positions:
            try:
                all_info = json.loads(ser.loc[attr])
                contour_area = all_info['contour_area']
                areas.append(contour_area)
            except:
                areas.append(-1)

        return areas

if __name__ == '__main__':
    data_folder = sys.argv[1]
    image_proc = PlantImageProc(output_dir='/home/iizuka/foodcomputer-vm/iizuka/output')
    output = pd.DataFrame()

    for f in tqdm(os.listdir(data_folder)):
        filepath = os.path.join(data_folder, f)
        shape_data_dict = image_proc.get_plant_data(filepath)
        if shape_data_dict is not None:
            for k, v in shape_data_dict.items():
                if isinstance(v, dict):
                    shape_data_dict[k] = json.dumps(v)

        shape_data_dict = pd.Series(shape_data_dict, name=f)
        output = output.append(shape_data_dict)


    output.to_csv('raw_result.csv')

    output.apply(
        get_contour_area, axis=1
    ).apply(
        pd.Series
    ).rename(
        columns = dict(zip(range(len(positions)), positions))
    ).to_csv('contour_area.csv')


