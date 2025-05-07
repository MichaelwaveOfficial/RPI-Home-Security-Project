from .BboxUtils import calculate_center_point, measure_euclidean_distance, calculate_detection_surface_area
from time import time 
from settings import * 


class ObjectTracking(object):

    ''' Module to parse detection data, track them by assigning IDs and pruning them when no longer required. '''

    def __init__(
            self,
            EUCLIDEAN_DISTANCE_THRESHOLD : int = 125,
            MAXIMUM_THREAT_LEVEL : int = DEFAULT_SETTINGS['motion_detection']['maximum_threat_threshold'],
            DEREGISTRATION_TIME : int = 4, ESCALATION_TIME : int = DEFAULT_SETTINGS['motion_detection']['threat_escalation_timer']
        ) -> None:
        
        '''
            Instantiate Object tracking module.

            Paramaters:
                * EUCLIDEAN_DISTANCE_THRESHOLD (int) : Distance between two points before they are classed as separate. 
                * MAXIMUM_THREAT_LEVEL (int) : Maximum threshold before a detection is considered a threat.
                * DEREGISTRATION_TIME (int) : Time taken in seconds before a detection is pruned to free up resources. 
                * ESCALATION_TIME (int) : Time taken in seconds for a detection to be present before its threat level is escalated.  
        '''
        
        # dictionary to hold detections data which can be used for IDs, bounding boxes and center points. 
        self.tracked_objects = {}

        # Assign unique ID values to each detection.
        self.ID_increment_counter : int = 1

        # Time taken for a detection to be deregistered.
        self.DEREGISTRATION_TIME = DEREGISTRATION_TIME

        # Minimum number of pixels between each center point before they are classed as new detections. 
        self.EUCLIDEAN_DISTANCE_THRESHOLD = (EUCLIDEAN_DISTANCE_THRESHOLD ** 2)

        # Maximum threat level allowed.
        self.MAXIMUM_THREAT_LEVEL =  MAXIMUM_THREAT_LEVEL

        # Time taken to escalate a detections threat level. 
        self.ESCALATION_TIME = ESCALATION_TIME

        self.max_center_points = 5

    
    def update_tracker(self, detections : list[dict]) -> list[dict]:

        ''' 
            Update the tracker by ingesting detections, comparing their center point values, checking whether or not they are the same. Otherwise,
            updating the entry classing it a fresh detection.
        
            Paramaters: 
                * detections : (list[dict]) : List encapsulating detection dictionary entries. 
            Returns:
                * parsed_detections : (list[dict]) : Parsed list of detection dictionaries with applied tracking processing.
        '''

        # If detections not of the expected type. Fail to run.
        if detections is None or not isinstance(detections, list):
            raise ValueError('Detections being parsed not a list of dictionaries.')

        # Get current time detections were being processed at. 
        updated_at = time()

        # Iterate over the current detections being ingested. 
        for current_detection in detections:
            
            # Calculate current, concerned detections center point value. 
            current_center_point = calculate_center_point(current_detection)

            # Check whether center point values match.
            matched_ID = self.match_detection_center_points(current_detection, current_center_point)

            # If an ID value is returned.
            if matched_ID is not None:

                # Update that detection object.
                self.update_object(matched_ID, current_detection, updated_at, current_center_point)

            else:
                # Otherwise, handle fresh detection.
                matched_ID = self.register_object(current_detection, updated_at, current_center_point)

            tracked_object = self.tracked_objects[matched_ID].copy()

            if matched_ID in self.tracked_objects:
                self.handle_detection_escalation(matched_ID, updated_at)

        # Check for objects that need pruning (exceed the threshold).
        self.prune_outdated_objects(updated_at)

        # Return list of parsed_detections.
        return list(self.tracked_objects.values())
    

    def match_detection_center_points(self, detection : dict, current_center_point : tuple[float, float]) -> int | None:

        '''
            Iterate over stored detection entries and detections being parsed. Compare their values to see if they are the 
            same or not. ID value is only returned if data matched is within the set thresholds.

            Paramaters:
                * detection : (dict) : Current detection being processed in dictionary form with its keys representing its metadata. 
                * current_center_point : (tuple[float, float]) : Current center point being calculated within the moment of processing.
            Returns:
                * detection_ID : (int | None) : If ruleset is matched, return ID value. Otherwise, return None. 
        '''

        # Initalise variables prior to use. 
        closest_ID = None 
        shortest_distance = float('inf')

        # Iterate over detections in the tracked_objects dictionary. 
        for ID, prev_detection in self.tracked_objects.items():
            
            # Fetch center point prior to the current. 
            previous_center = prev_detection['center_points'][-1]

            # Get the straight line distance between both center points. 
            euclidean_distance_squared = measure_euclidean_distance(current_center_point, previous_center)

            # Get the detections bbox width and height.
            detection_width = abs(detection['x2'] - detection['x1'])

            # Scale the euclidean distance threshold in accordance to the detections dimensions. 
            scaled_euclidean_distance_threshold = self.EUCLIDEAN_DISTANCE_THRESHOLD * detection_width

            # If distance within the threshold and threshold SQUARED less than shorted distance.
            if euclidean_distance_squared <= scaled_euclidean_distance_threshold and \
                euclidean_distance_squared < shortest_distance:

                # Assign ID value as the closest.
                closest_ID = ID 
                # Assign shortest distance as the current straight line distance.
                shortest_distance = euclidean_distance_squared

        # Return the ID value. 
        return closest_ID
    

    def register_object(self, detection : dict, seen_at : float, current_center_point : tuple[float, float]) -> None:

        '''
            Reigster fresh detection entry within the tracked_objects dictionary with current metadata
            at the time of processing. 

            Paramaters:
                * detection : (dict) : Current detection dictionary from ingested list.
                * seen_at : (float) : time detection is being processed at. 
                * current_center_point : (tuple[float, float]) : Current center x and y values at time of processing.
            Returns:
                * None
        '''

        new_ID = self.ID_increment_counter

        # Assign ID value to dictionary entry and required metadata.
        self.tracked_objects[self.ID_increment_counter] = {
            'ID' : self.ID_increment_counter,
            'center_points' : [current_center_point],
            'bboxes' : {
                'x1': detection['x1'],
                'y1': detection['y1'],
                'x2': detection['x2'],
                'y2': detection['y2']
            },
            'first_detected' : seen_at,
            'last_detected' : seen_at,
            'last_escalated' : seen_at,
            'threat_level' : 0
        }
    
        # Increment counter to keep ID values unique.
        self.ID_increment_counter += 1

        return new_ID
    

    def update_object(self, ID : int, detection : dict, updated_at : float, current_center_point : tuple[float, float]) -> None:

        '''
            Function to ingest detection data and update its relevant values whilst it is still concerned in the tracked objects
                dictionary.

            Paramaters:
                * ID : (int) : Detections unique identifier.
                * detection : (dict) : Detection dictionary encapsulating its metadata.
                * updated_at : (float) : Current time detection is being processed at.
                * current_center_point : (tuple[float, float]) : Current detections center point value at the time of processing.
            Returns:
                * None
        '''

        # Append current center point value to detection center points list. 
        self.tracked_objects[ID]['center_points'].append(current_center_point)

        # Maintain a rolling window of last five velocity values. 
        if len(self.tracked_objects[ID]['center_points']) > self.max_center_points:
            self.tracked_objects[ID]['center_points'].pop(0)

        # Update time detection was last seen.
        self.tracked_objects[ID]['last_detected'] = updated_at

        self.tracked_objects[ID]['bboxes'] = {
            'x1': detection['x1'],
            'y1': detection['y1'],
            'x2': detection['x2'],
            'y2': detection['y2']
        }  
        
        # Update detection dictionary with its entry within the tracked_objects dictionary.
        detection.update(self.tracked_objects[ID])

    
    def prune_outdated_objects(self, updated_at : float) -> None:

        '''
            Iterate over parameterised detections and prune those exceeding the set time limit threshold.

            Parameters:
                * parsed_detections : list[dict] -> list of detection data entries.
            Returns:
                * None. 
        '''

        # Initialise list to store ID values of detections to be pruned. 
        stale_detections = [ID for ID, detection in self.tracked_objects.items()
                            if (updated_at - detection['last_detected']) > self.DEREGISTRATION_TIME]

        # Iterate over the IDs present. 
        for ID in stale_detections:
            # Use IDs to delete entries from tracked objects. 
            del self.tracked_objects[ID]


    def update_settings(self, settings : dict):

        ''' Apply user configuaration settings to camera ''' 

        self.settings = settings.get('motion_detection', {})
        self.MAXIMUM_THREAT_LEVEL = self.settings.get('maximum_threat_threshold')
        self.ESCALATION_TIME = self.settings.get('threat_escalation_timer')


    def handle_detection_escalation(self, ID : int, updated_at : float) -> None:

        detection = self.tracked_objects[ID]

        elapsed_time = (updated_at - detection['first_detected'])
        last_escalation_time = (updated_at - detection['last_escalated'])

        if elapsed_time >= self.ESCALATION_TIME \
            and last_escalation_time >= self.ESCALATION_TIME:

            detection['threat_level'] += 1
            detection['last_escalated'] = updated_at

            if detection['threat_level'] > self.MAXIMUM_THREAT_LEVEL:
                # Report detection.
                print(f'Detection {ID} exceeded maximum threat level.')
                del self.tracked_objects[ID]
