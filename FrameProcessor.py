
from utils.Camera import Camera
from utils.Annotate import Annotations
from utils.ObjectDetection import ObjectDetection
from utils.ObjectTracking import ObjectTracking

import cv2 

class FrameProcessor(object):

    ''' Pipeline processing class. '''

    def __init__(self, camera : Camera):

        ''' camera : Camera - Camera object. '''

        self.camera = camera
        self.annotations = Annotations()
        self.object_detection = ObjectDetection()
        self.object_tracking = ObjectTracking()

    
    def generate_frames(self):

        ''' Generator function to yield JPEG fames encoded for Flask web server streaming. '''

        try:
            
            prev_raw_frame = None
            raw_frame = None
            current_detection = None

            while True:
                
                # Fetch frame from camera.
                raw_frame = self.camera.read_frame()
                annotated_frame = raw_frame.copy()

                # Pursue detection logic is both current & previous frames are available.
                if prev_raw_frame is not None:
                    
                    # Return detection bounding boxes.
                    detection_bboxes = self.object_detection.detect_motion(prev_raw_frame, raw_frame)[1]

                    # If bounding boxes returned.
                    if detection_bboxes:
                        
                        # Track the detections by assigning IDs.
                        tracked_detections = self.object_tracking.update_tracker(detection_bboxes)

                        # Annotate detections in frame with processed detection data. 
                        annotated_frame = self.annotations.annotate_frame(frame=raw_frame, detections=tracked_detections)
                    
                # Update previous frame with current.
                prev_raw_frame = raw_frame

                # Switch colour channels RGB -> BGR.
                annotated_frame = self.convert_frame_colour_channels(annotated_frame)

                # Encode raw frame.
                encoded_frame = self.encode_frame_2_jpeg(annotated_frame)

                # Yield that frame for streaming.
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + encoded_frame + b'\r\n'
                )

        except GeneratorExit:

            # Handle failuer gracefully.
            print('Camera client has since disconnected.')

        finally:

            # Resource clean up.
            self.camera.close_camera()

    
    def encode_frame_2_jpeg(self, frame):

        ''' Encode parsed frame '''

        success, buffer = cv2.imencode('.jpg', frame)

        if not success:
            raise ValueError('Failed to encode frame, please check input.')

        return buffer.tobytes()

    
    def convert_frame_colour_channels(self, frame):

        ''' Switch colour channels to prevent confusion. '''

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    
    def update_modules_settings(self, settings : dict):

        ''' Update module objects initialised in pipelines. '''

        modules_map = {
            'stream_quality' : (self.camera, 'update_settings'),
            'motion_detection' : (self.object_detection, 'update_settings'),
            #alerts: (self.alerts, 'update_settings),
            #client: (self.client_comms, 'update_settings') THESE ARE FOR LATER EXPANSION.
        }

        for key, (module, method) in modules_map.items():

            module_config = settings.get(key, {})

            getattr(module, method)(module_config)
