import cv2
import numpy as np
import plantcv as pcv
from matplotlib import pyplot as plt


class PlantImageProc():
    def __init__(self, output_dir='/home/iizuka/foodcomputer-vm/output',
                hyper_parameters={}, debug=None, is_save_img=True):
        '''
        output_dir : directory where output files are located
        hyper_parameters : hyper parameters relevant of image processing, type is dictionary,
            attributes are , rotate_angle, bin_threshold, fill_threshold, kernel_size
        roi : area of region of interest, type is dictironary
            attributes are, x, y , width, height
        debug : 3 str values are possible,
            'plot' -> show image when uesd in jupyter notebook
            'print' -> save every image at output_dir
            None -> generate no image
        is_save_img : type is boolean. if true, generate image with contours at
        output_dir
        '''
        self.device = 0
        if not hyper_parameters:
            hyper_parameters = {
                'rotate_angle':45,
                'bin_threshold':120,
                'fill_threshold':2500,
                'kernel_size':11,
                'roi':{
                    'x':400, 'y':100, 'width':-450, 'height':-170
                }
            }
        self.hyper_parameters = hyper_parameters
        self.debug = debug
        self.output_dir =output_dir
        self.pos_list =  ['top', 'left', 'right', 'bottom']
        self.is_save_img = is_save_img
        self.error_list = set(['night_image', 'process_fail'])
        self.default_obj = {pos:None for pos in self.pos_list}


    def get_plant_data(self, img_file, hyper_parameters={}, debug=None):
        contours_dict = self.get_contours_dict(img_file, hyper_parameters=hyper_parameters, debug=debug)
        if type(contours_dict) is str:
            if contours_dict in self.error_list:
                error = contours_dict
                return {pos:{'error_type':error} for pos in self.pos_list}
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

    def get_contours_dict(self, img_file, hyper_parameters={}, debug=None):
        device = self.device
        output_dir = self.output_dir
        if not hyper_parameters:
            hyper_parameters = self.hyper_parameters
        img, path, filename = pcv.readimage(img_file)
        if np.average(img) < 50:
            return 'night_image'

        try:
            device,img=pcv.white_balance(device,img,debug,roi=(50,0,1000,600))

            rotate_angle = hyper_parameters['rotate_angle']
            device, img = pcv.rotate_img(img, rotate_angle, device, debug)

            device, b = pcv.rgb2gray_lab(img,  'b', device, debug)
            b -= self.get_inverted_bin_img(img, hyper_parameters['rotate_angle'])
            bin_threshold = hyper_parameters['bin_threshold']
            device, img_binary = pcv.binary_threshold(b, bin_threshold , 255, 'light', device, debug)

            # fille small objects
            fill_threshold = hyper_parameters['fill_threshold']
            mask = np.copy(img_binary)
            device, fill_image = pcv.fill(img_binary, mask, fill_threshold, device, debug)
            #  dilate objects
            # device, dilated = pcv.dilate(fill_image, 1, 1, device, debug)
            # apply median filter
            kernel_size = hyper_parameters['kernel_size']
            device, blur = pcv.median_blur(fill_image, kernel_size, device, debug=debug)
            # find objects
            device, id_objects, obj_hierarchy = pcv.find_objects(img, blur, device, debug)
            # define region of interest
            roi = hyper_parameters['roi']
            device, roi, roi_hierarchy = pcv.define_roi(img, 'rectangle', device, None, 'default', debug, True,
                                                         roi['x'], roi['y'], roi['width'], roi['height'])
            device, roi_objects, roi_obj_hierarchy, kept_mask, obj_area = pcv.roi_objects(img, 'partial', roi, roi_hierarchy,
                                                                                       id_objects, obj_hierarchy, device,
                                                                                       debug)

            # get clusters_i and contours
            # clusters_i is 2d list , axis0 represents index of cluster, and axis1 represents contour index within its cluster.
            # TODO if cluster size is not 4, use function "analyze_bound" to manually draw the area
            device, clusters_i, contours = pcv.cluster_contours(device, img, roi_objects, 2, 2, debug)
            # device, output_path = pcv.cluster_contour_splitimg(device, img, clusters_i,
            #                                                 contours, output_dir, file=filename, filenames=None, debug=debug)
            contours_dict = self.make_contours_dict_from_clusters(clusters_i, contours)
            if self.is_save_img:
                img_filename = img_file.split('.')[0].split('/')[-1]
                self.save_img_with_contour(img, img_binary, contours_dict, img_filename, output_dir, device, debug)
            return contours_dict
        except:
            return 'process_fail'

        '''
        # follwoing code can be applied to get analayzed object
        device, shape_header, shape_data, shape_img = pcv.analyze_object(
        img, 'hoge.jpg', contour, blur, self.device, self.debug, 'hoge1.jpg')
        '''


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

    def save_img_with_contour(self, img, mask, contours_dict, img_filename, output_dir, device, debug):
        contours = [contours_dict[pos] for pos in self.pos_list]
        cv2.drawContours(img, contours, -1, (255,0,0), 3)
        device, masked_img = pcv.apply_mask(img, mask, 'white', device, debug)
        cv2.imwrite('{}/{}_contours.jpg'.format(output_dir, img_filename), masked_img)

    def get_inverted_bin_img(self, img, rotate_angle):
        white_img = img.copy()
        white_img[:,:,0:3] = (255,255,255)
        self.device, white_rotate_img = pcv.rotate_img(white_img, rotate_angle, self.device, self.debug)
        inverted_img = cv2.bitwise_not(white_rotate_img)
        return inverted_img[:,:,0] / 255 * 127
