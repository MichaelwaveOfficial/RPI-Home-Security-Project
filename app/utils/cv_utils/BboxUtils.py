import numpy as np


def unpack_bbox_values(detection):

    if isinstance(detection, dict) and len(detection) == 4:

        x1, y1, x2, y2 = int(detection['x1']), int(detection['y1']), int(detection['x2']), int(detection['y2'])

    elif isinstance(detection, dict) and len(detection) > 4:

        x1, y1, x2, y2 = int(detection['bboxes']['x1']), int(detection['bboxes']['y1']), int(detection['bboxes']['x2']), int(detection['bboxes']['y2'])
    
    elif isinstance(detection, (list, tuple, np.ndarray)):

        x1, y1, x2, y2 = detection[:4]

    else:

        raise ValueError('Invalid Inputs do not match required formats -> Dictionary, List, Tuple, Numpy')

    return x1, y1, x2, y2


def calculate_center_point(detection):

    '''
        Simple function to calculate the center point of a given detection. This can be useful for both 
        annotation and tracking purposes. 

        Parameters:
            * bbox : dict -> the detections metadata to calculate the center point. 

        Returns: 
            * center_x, center_y : tuple -> two floating point values representing the detections center 
                on the x and y axis. 
    '''

    x1, y1, x2, y2 = unpack_bbox_values(detection)
    
    center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2

    return int(center_x), int(center_y)


def measure_euclidean_distance(p1, p2):

    '''
        Function to measure the straight-line distance between two points. Gets the sqaure values of the inputs and sqaures the output
            to help reduce computation. 

        Paramaters:
            * p1 : tuple -> (x1, y1), detection start position.
            * p2 : tuple -> (x2,y2), detection end position.

        Returns:
            * euclidean_distance : float -> distance between one position and another. 
    '''

    return (p1[0] - p2[0]) **2 + (p1[1] - p2[1]) **2


def calculate_detection_surface_area(detection):

    x1, y1, x2, y2 = unpack_bbox_values(detection)

    width, height = (x1 + x2), (y1 + y2)

    return (width * height)
