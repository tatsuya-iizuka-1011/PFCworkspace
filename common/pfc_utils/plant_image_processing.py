import sys
#inclue plantcv path
PLANTCV_PATH = '/home/iizuka/workspace/py2/lib/plantcv'
sys.path.append(PLANTCV_PATH)

import cv2
import numpy as np
import plantcv as pcv


SHAPES_PROPERTIES = (
    'name',
    'object_area',
    'convex-hull_area',
    'solidity',
    'object_perimeter_length',
    'object_width_(extent_x)',
    'object_height_(extent_y)',
    'longest_axis',
    'center_of_mass-x',
    'center_of_mass-y',
    'hull_vertices',
    'in_bounds',
    'object_bounding_ellipse_center-x',
    'object_bounding_ellipse_center-y',
    'object_bounding_ellipse_major_axis',
    'object_bounding_ellipse_minor_axis',
    'object_bounding_ellipse_angle',
    'object_bounding_ellipse_eccentricity',
)
DEFAULT_OUTPUT_DIR = '/home/iizuka/workspace/py2/generated_imgs/plantcv'


class PlantImageProc():
    def __init__(self, plant_pos=None, bin_threshold=107, margin=30,
                 output_dir=DEFAULT_OUTPUT_DIR):
        self.device = 0
        self.dark_threshold = 50
        self.bin_threshold = bin_threshold
        if plant_pos is None:
            self.hyper_parameters =self.get_default_hyperparam()

        self._plant_pos = plant_pos
        self.margin = margin
        self.output_dir = output_dir

    @property
    def hyper_parameters(self):
        if self._plant_pos is None:
            if self._hyper_parameters:
                return self._hyper_parameters
            else:
                print('hyper_parameter is default value')
                return self.get_default_hyperparam()
        else:
            return  self.make_hyper_params_from_pos(self._plant_pos,
                                                                bin_threshold=self.bin_threshold, margin=self.margin)

    @hyper_parameters.setter
    def hyper_parameters(self, hyper_parameters):
        self._hyper_parameters = hyper_parameters

    def set_plant_pos(self, plant_pos):
        self._plant_pos = plant_pos

    def get_default_hyperparam(self):
        hyper_parameters = {
            'bin_threshold':107,
            'roi':{
                'left':{'x':200, 'y':300, 'width':-800, 'height':-150},
                'right':{'x':800, 'y':300, 'width':-350, 'height':-150},
                'top':{'x':550, 'y':0, 'width':-600, 'height':-600}
            }
        }
        return hyper_parameters

    def get_shapedata_dict(self, shape_data):
        if len(shape_data) == len(SHAPES_PROPERTIES):
            shape_dict = {prop:shape_data[i] for i, prop in enumerate(SHAPES_PROPERTIES)}
            return shape_dict
        else:
            print('length of shape data is not compatible')

    def get_plant_data(self, img_file, hyper_parameters=None, debug_list=[], count=0):
        debug = None
        debug_dict = self.get_debug_dict(debug_list)
        if hyper_parameters is None:
            hyper_parameters = self.hyper_parameters
        img, path, filename = pcv.readimage(img_file)
        device = 0
        shape_data_dict = {}
        if np.average(img) < self.dark_threshold:
            #pcv.fatal_error("Night Image{}".format(img_file))
            return None
        else:
            pass
        for pos in hyper_parameters['roi']:
            #following variable needs to be given
            device, b = pcv.rgb2gray_lab(img, 'b', device, debug_dict['rgb2gray_lab'] )
            device, b_cnt = pcv.binary_threshold(b, hyper_parameters['bin_threshold'], 255, 'light',
                                                 device, debug_dict['rgb2gray_lab'] )
            device, masked = pcv.apply_mask(img, b_cnt, 'white', device, debug_dict['apply_mask'] )
            device, id_objects,obj_hierarchy = pcv.find_objects(masked, b_cnt, device, debug_dict['find_objects'] )
            params = hyper_parameters['roi'][pos]
            device, roi1, roi_hierarchy= pcv.define_roi(
                masked, 'rectangle', device, None, 'default',
                debug_dict['define_roi'] , True, params['x'], params['y'], params['width'], params['height'])
            device,roi_objects, hierarchy3, kept_mask, obj_area = pcv.roi_objects(
                img, 'partial', roi1, roi_hierarchy,
                id_objects, obj_hierarchy, device, debug_dict['roi_objects'] )
            device, obj, mask = pcv.object_composition(
                img, roi_objects, hierarchy3, device, debug_dict['object_composition'])
            filename = 'img_{}.jpg'.format(pos)
            try:
                device, shape_header, shape_data, shape_img = pcv.analyze_object(
                    img, 'hoge.jpg', obj, b_cnt, device,
                    debug_dict['analyze_object'], self.output_dir + '/' + filename)
                shape_data_dict[pos] = self.get_shapedata_dict(shape_data)
                shape_data_dict[pos]['contour_area'] = cv2.contourArea(obj)
                #print('area of {} is {}'.format(pos,  shape_data_dict[pos]['contour_area'] ))
            except:
                shape_data_dict[pos] = None

        return shape_data_dict

    def make_hyper_params_from_pos(self, plant_pos, bin_threshold=107, margin=50):
        IMG_SHAPE = (720,1280,3)
        pos_list = [pos for pos in plant_pos]
        default_plant_pos = {
            'left':[400,350],
            'top':[650, 100],
            'right':[880, 350],
            'bottom':[650,550]
        }
        new_plant_pos = {}
        for pos in default_plant_pos:
            if pos not in plant_pos:
                new_plant_pos[pos] = default_plant_pos[pos]
        new_plant_pos.update(plant_pos)
        hyper_parameters = {}
        hyper_parameters['roi'] = {}
        for pos in pos_list:
            if pos =='left' or pos == 'right':
                hyper_parameters['roi'] [pos] = {'x':new_plant_pos[pos][0]-margin, 'y':new_plant_pos['top'][1],
                    'width':new_plant_pos[pos][0]+margin-IMG_SHAPE[1], 'height':new_plant_pos['bottom'][1]-IMG_SHAPE[0]}
            elif pos =='top' or pos == 'bottom':
                hyper_parameters['roi'] [pos] = {'x':new_plant_pos['left'][0], 'y':new_plant_pos[pos][1]-margin,
                    'width':new_plant_pos['right'][0]-IMG_SHAPE[1], 'height':new_plant_pos[pos][1]+margin-IMG_SHAPE[0]}
        hyper_parameters['bin_threshold'] = bin_threshold
        return hyper_parameters

    def test_roi(self, img_file, plant_pos=None,  hyper_parameters=None):
        if hyper_parameters is None and plant_pos is None:
            print('please specify hyper_parameters or plant_pos')
            return False
        elif plant_pos is not None:
            hyper_parameters = self.make_hyper_params_from_pos(plant_pos=plant_pos)
        debug_list = ['define_roi', 'object_composition']
        return self.get_plant_data(img_file, hyper_parameters, debug_list=debug_list)

    def get_debug_dict(self, debug_list, default=None):
        func_set = set(('rgb2gray_lab', 'binary_threshold', 'apply_mask', 'find_objects', 'define_roi',
                        'roi_objects', 'object_composition', 'analyze_object'))
        debug_dict = {}
        for func in func_set:
            debug_dict[func]  = 'plot' if func in debug_list else default
        return debug_dict
