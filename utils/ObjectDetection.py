import cv2 
import os
import numpy as np
from .BboxUtils import calculate_center_point, measure_euclidean_distance
from settings import *

class ObjectDetection(object):

    '''
        Utilities leveraging more traditional computer vision techniques to mitigate over exhaustion of the pi due to its resource constraints
            whilst running in real time. 

        On top of this, helper functions pertaining to the handling of detections can also be found within this module. 
    '''

    def __init__(self):

        self.settings = {}
        self.sensisitvity = DEFAULT_SETTINGS['motion_detection']['sensitivity'] # Min contour area.


    def pre_process_frame(self, frame : np.ndarray) -> np.ndarray:

        ''' preprocess frame before it is analysed further. '''

        # Convert the frame to greyscale to reduce colours channels, in turn reducing processing.
        frame_greyscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply gaussian filter to reduce noise in an attempt to mitigate false positives. 
        frame_blur = cv2.GaussianBlur(frame_greyscale, (9, 9), 1.5)

        # Cull salt & pepper noise.
        frame_smoothed = cv2.medianBlur(frame_blur, 3)

        return frame_smoothed


    def detect_motion(self, prev_frame : np.ndarray, curr_frame : np.ndarray, binarisation_threshold : int = 105) -> tuple[np.ndarray, list[np.ndarray]]:

        ''' Detect motion in frame utilising traditional computer vision techniques. '''

        bboxes = []

        # Check frames passed are not None Type. Raise exception if they are. 
        if curr_frame is None or prev_frame is None:
            raise ValueError('Provided frames were returned as None!')

        # Preprocess frames for operating upon.
        curr_frame = self.pre_process_frame(curr_frame)
        prev_frame = self.pre_process_frame(prev_frame)

        # Compute absolute difference between current and previous frames. 
        frame_difference = cv2.absdiff(prev_frame, curr_frame)
        # Apply a binary threshold to fetch regions with significant change within the frame.
        _, frame_thresholded = cv2.threshold(frame_difference, binarisation_threshold, 255, cv2.THRESH_BINARY)

        # Initialise kernel for morphological operations.
        kernel = np.ones((3, 3), np.uint8)
        # Dilate on the thresholded frame to fill in the gaps and solidify contour areas.
        frame_dilation = cv2.dilate(frame_thresholded, kernel, iterations=1)

        # Fetch regions in the frame where motion has been detected. 
        contours = cv2.findContours(frame_dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        # Store list of detected motion areas.
        filtered_contours = [contour for contour in contours if (cv2.contourArea(contour)) > (self.sensisitvity)]
        
        # Iterate over the filtrated detections.
        for contour in filtered_contours:
            
            # Use opencv to draw a bounding box around the detected contour, unpack its values. 
            x1, y1, w, h = cv2.boundingRect(contour)

            # Append these values to a dictionary for each detection. Convert to x1, y1, x2, y2 format.
            bboxes.append({'x1' : int(x1), 'y1' : int(y1), 'x2' : int(x1 + w), 'y2' : int(y1 + h)})

        bboxes = self.compile_small_contours(bboxes)

        # Return process frame and parsed bounding boxes
        return frame_dilation, bboxes
    

    def compile_small_contours(self, bboxes, merge_distance = 100):

        ''' '''

        if not bboxes:
            return []

        np_bboxes = np.array([[box['x1'], box['y1'], box['x2'], box['y2']] for box in bboxes])

        merged_contours = []
        used = set()

        for index_a, box_a in enumerate(np_bboxes):

            if index_a in used:
                continue

            center_point_a = calculate_center_point(box_a)

            merge_group = [box_a]
            used.add(index_a)

            for index_b, box_b in enumerate(np_bboxes):

                if index_b in used or index_a == index_b:
                    continue

                center_point_b = calculate_center_point(box_b)

                euclidean_distance_squared = measure_euclidean_distance(center_point_a, center_point_b)

                if euclidean_distance_squared < (merge_distance ** 2):

                    merge_group.append(box_b)
                    used.add(index_b)

            group_array = np.array(merge_group)

            merged_x1 = int(np.min(group_array[:, 0]))
            merged_y1 = int(np.min(group_array[:, 1]))
            merged_x2 = int(np.max(group_array[:, 2]))
            merged_y2 = int(np.max(group_array[:, 3]))

            merged_contours.append({'x1': merged_x1, 'y1': merged_y1, 'x2': merged_x2, 'y2': merged_y2})

        return merged_contours

    
    def update_settings(self, settings : dict):

        ''' Apply user configuaration settings to camera ''' 

        self.settings = settings

        self.sensisitvity = settings.get('sensitivity')
