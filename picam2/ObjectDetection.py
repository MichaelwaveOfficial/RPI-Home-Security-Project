import cv2 
import os
import numpy as np

class ObjectDetection(object):

    '''
        Utilities leveraging more traditional computer vision techniques to mitigate over exhaustion of the pi due to its resource constraints
            whilst running in real time. 

        On top of this, helper functions pertaining to the handling of detections can also be found within this module. 
    '''

    def __init__(self, min_contour_area : int):
        self.min_contour_area = min_contour_area


    def process_frame(self, frame : np.ndarray) -> np.ndarray:

        ''' preprocess frame before it is analysed further. '''

        # Convert the frame to greyscale to reduce colours channels, in turn reducing processing.
        frame_greyscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply gaussian filter to reduce noise in an attempt to mitigate false positives. 
        return cv2.GaussianBlur(frame_greyscale, (21, 21), 0)


    def detect_motion(self, prev_frame : np.ndarray, curr_frame : np.ndarray, binarisation_threshold : int = 25) -> tuple[np.ndarray, list[np.ndarray]]:

        ''' Detect motion in frame utilising traditional computer vision techniques. '''

        bboxes = []

        # Check frames passed are not None Type. Raise exception if they are. 
        if curr_frame is None or prev_frame is None:
            return ValueError('Provided frames were returned as None!')

        curr_frame = self.process_frame(curr_frame)
        prev_frame = self.process_frame(prev_frame)

        # Compute absolute difference between current and previous frames. 
        frame_difference = cv2.absdiff(prev_frame, curr_frame)

        # Apply a binary threshold to fetch regions with significant change within the frame.
        _, frame_thresholded = cv2.threshold(frame_difference, binarisation_threshold, 255, cv2.THRESH_BINARY)

        # Dilate on the thresholded frame to fill in the gaps and solidify contour areas.
        frame_dilation = cv2.dilate(frame_thresholded, None, iterations=5)

        # Fetch regions in the frame where motion has been detected. 
        contours = cv2.findContours(frame_dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        # Store list of detected motion areas.
        filtered_contours = [contour for contour in contours if cv2.contourArea(contour) > self.min_contour_area]
        
        # Select the largest detected contour from the filtered list.
        largest_contour = max(filtered_contours, key=cv2.contourArea, default=None)

        # Mitigate bugs, ensure largest contour has been found.
        if largest_contour is not None:
            
            # Unpack detection bounding box values from largest contour.
            x1, y1, w, h = cv2.boundingRect(largest_contour)

            # Append these values to a dictionary for each detection. Convert to x1, y1, x2, y2 format.
            detection = {'x1' : int(x1), 'y1' : int(y1), 'x2' : int(x1 + w), 'y2' : int(y1 + h)}

            # Add to bboxes list.
            bboxes.append(detection)

        """# Iterate over the filtrated detections.
        for contour in filtered_contours:
            
            # Use opencv to draw a bounding box around the detected contour, unpack its values. 
            x1, y1, w, h = cv2.boundingRect(contour)

            # Append these values to a dictionary for each detection. Convert to x1, y1, x2, y2 format.
            detection = {'x1' : int(x1), 'y1' : int(y1), 'x2' : int(x1 + w), 'y2' : int(y1 + h)}

            # Add to bboxes list.
            bboxes.append(detection)"""

        # Return process frame and parsed bounding boxes
        return frame_dilation, bboxes


    def annotate_detections(self, frame : np.ndarray, contours : list[np.ndarray]) -> np.ndarray:

        ''' Iterate over the passed frames, their associated areas where motion has been detected and annotate that movement. '''

        # Create a copy of the frame for operating upon. 
        annotated_frame = frame.copy()

        # Iterate each detections contours.
        for detection in contours:

            # Annotate a bounding boxes corners onto the detection within the frame.
            annotated_frame = self.annotate_bbox_corners(annotated_frame, detection)

        return annotated_frame
