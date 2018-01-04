import cv2
import numpy as np
import plantcv as pcv
from matplotlib import pyplot as plt
input_img_path = '/home/iizuka/foodcomputer-vm/iizuka/input'


class PlantImageProc():
    def __init__(self, output_dir='/home/iizuka/foodcomputer-vm/output',
                hyper_parameters={}, debug=None, is_save_img=True):
        self.device = 0
        if not hyper_parameters:
            hyper_parameters = {
                'rotate_angle':45,
                'bin_threshold':160,
                'fill_threshold':1000,
                'roi':{
                    'x':400, 'y':100, 'width':-450, 'height':-170
                }
            }
        self.hyper_parameters = hyper_parameters
        self.debug = debug
        self.output_dir =output_dir
        self.pos_list =  ['top', 'left', 'right', 'bottom']
        self.is_save_img = is_save_img
        self.default_obj = {pos:None for pos in self.pos_list}



    def get_plant_data(self, img_file, hyper_parameters={}):
        contours_dict = self.get_contours_dict(img_file, hyper_parameters=hyper_parameters)
        if contours_dict is None:
            return self.default_obj
        analyed_obj = {}
        for pos in contours_dict:
            contour = contours_dict[pos]
            obj = {}
            obj['contour_area'] = cv2.contourArea(contour)
            M = cv2.moments(contour)
            obj['moment_x'] = int(M['m10']/M['m00'])
            obj['moment_y'] = int(M['m01']/M['m00'])
            analyed_obj[pos] = obj
        return analyed_obj

    def get_contours_dict(self, img_file, hyper_parameters={}):
        device = self.device
        debug = self.debug
        output_dir = self.output_dir
        if not hyper_parameters:
            hyper_parameters = self.hyper_parameters
        img, path, filename = pcv.readimage(img_file)
        if np.average(img) < 50:
            return None
        else:
            pass
        try:
            rotate_angle = hyper_parameters['rotate_angle']
            device, rotate_img = pcv.rotate_img(img, rotate_angle, device, debug)
            img = rotate_img
            device, a = pcv.rgb2gray_lab(img,  'a', device, debug)

            bin_threshold = hyper_parameters['bin_threshold']
            device, img_binary = pcv.binary_threshold(a, bin_threshold , 255, 'dark', device, debug)

            # fille small objects
            fill_threshold = hyper_parameters['fill_threshold']
            mask = np.copy(img_binary)
            device, fill_image = pcv.fill(img_binary, mask, fill_threshold, device, debug)
            #  dilate objects
            device, dilated = pcv.dilate(fill_image, 1, 1, device, debug)
            # find objects
            device, id_objects, obj_hierarchy = pcv.find_objects(img, dilated, device, debug)
            # define region of interest
            roi = hyper_parameters['roi']
            device, roi, roi_hierarchy = pcv.define_roi(img, 'rectangle', device, None, 'default', debug, True,
                                                         roi['x'], roi['y'], roi['width'], roi['height'])
            device, roi_objects, roi_obj_hierarchy, kept_mask, obj_area = pcv.roi_objects(img, 'partial', roi, roi_hierarchy,
                                                                                       id_objects, obj_hierarchy, device,
                                                                                       debug)

            # get clusters_i and contours
            # clusters_i is 2d list , axis0 represents index of cluster, and axis1 represents contour index within its cluster.
            device, clusters_i, contours = pcv.cluster_contours(device, img, roi_objects, 2, 2, debug)
            # device, output_path = pcv.cluster_contour_splitimg(device, img, clusters_i,
            #                                                   contours, output_dir, file=filename, filenames=None, debug=debug)
            if self.is_save_img:
                img_filename = img_file.split('.')[0].split('/')[-1]
                self.save_img_with_contour(img, img_binary, contours, img_filename, output_dir, device, debug)

            return self.make_contours_dict_from_clusters(clusters_i, contours)
        except:
            print('image processing error')
            return None

    def make_contours_dict_from_clusters(self, clusters_i, contours):
        pos_list = self.pos_list
        contour_dict = {}
        for pos_index, cluster in enumerate(clusters_i):
            max_index = -1
            if len(cluster) == 1:
                max_index = cluster[0]
            else:
                lai = -1
                for i in cluster:
                    tmp_lai = cv2.contourArea(contours[i])
                    if tmp_lai > lai :
                        max_index = i
                        lai = tmp_lai
            contour_dict[pos_list[pos_index]] = contours[max_index]
        return contour_dict

    def save_img_with_contour(self, img, mask, contours, img_filename, output_dir, device, debug):
        cv2.drawContours(img, contours, -1, (255,0,0), 3)
        device, masked_img = pcv.apply_mask(img, mask, 'white', device, debug)
        cv2.imwrite('{}/{}_contours.png'.format(output_dir, img_filename), masked_img)
