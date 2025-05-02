import cv2 
import os
import numpy as np
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
        frame_blur = cv2.GaussianBlur(frame_greyscale, (7, 7), 0)

        # Cull salt & pepper noise.
        frame_smoothed = cv2.medianBlur(frame_blur, 3)

        return frame_smoothed


    def detect_motion(self, prev_frame : np.ndarray, curr_frame : np.ndarray, binarisation_threshold : int = 25) -> tuple[np.ndarray, list[np.ndarray]]:

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
        kernel = np.ones((6, 6), np.uint8)
        # Dilate on the thresholded frame to fill in the gaps and solidify contour areas.
        frame_dilation = cv2.dilate(frame_thresholded, kernel, iterations=3)

        # Fetch regions in the frame where motion has been detected. 
        contours = cv2.findContours(frame_dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        # Store list of detected motion areas.
        filtered_contours = [contour for contour in contours if (cv2.contourArea(contour) **2) > (self.sensisitvity ** 2)]
        
        # Iterate over the filtrated detections.
        for contour in filtered_contours:
            
            # Use opencv to draw a bounding box around the detected contour, unpack its values. 
            x1, y1, w, h = cv2.boundingRect(contour)

            # Append these values to a dictionary for each detection. Convert to x1, y1, x2, y2 format.
            bboxes.append({'x1' : int(x1), 'y1' : int(y1), 'x2' : int(x1 + w), 'y2' : int(y1 + h)})

        bboxes = self.compile_small_contours(bboxes)

        # Return process frame and parsed bounding boxes
        return frame_dilation, bboxes
    

    def compile_small_contours(self, bboxes, merge_distance = 1200):

        ''' '''

        if not bboxes:
            return []

        np_bboxes = np.array([[box['x1'], box['y1'], box['x2'], box['y2']] for box in bboxes])

        merged_contours = []
        used = set()

        for index_a, box_a in enumerate(np_bboxes):

            if index_a in used:
                continue

            x1, y1, x2, y2 = box_a 

            for index_b, box_b in enumerate(np_bboxes):

                if index_b in used or index_a == index_b:
                    continue

                x1_b, y1_b, x2_b, y2_b = box_b

                if (
                    (abs(x1 - x1_b) ** 2) < (merge_distance ** 2)
                    and (abs(y1 - y1_b) ** 2) < (merge_distance ** 2)
                    and (abs(x2 - x2_b) ** 2) < (merge_distance ** 2)
                    and (abs(y2 - y2_b) ** 2) < (merge_distance ** 2)
                ):

                    x1, y1, x2, y2 = max(x1, x1_b), max(y1, y1_b), min(x2, x2_b), min(y2, y2_b)
                    used.add(index_b)

            merged_contours.append({'x1' : x1, 'y1' : y1, 'x2' : x2, 'y2' : y2})
            used.add(index_a)

        return merged_contours

    
    def update_settings(self, settings : dict):

        ''' Apply user configuaration settings to camera ''' 

        self.settings = settings

        self.sensisitvity = settings.get('sensitivity')
