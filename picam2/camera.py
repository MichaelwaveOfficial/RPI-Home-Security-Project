
import io 
import picamera2
import cv2
from ObjectDetection import ObjectDetection
from Annotate import Annotations


class Camera(object):

    ''' Camera class to access and manipulate the devices onboard camera. '''

    def __init__(self, resolution : tuple[int, int], framerate : int, content_type : str, use_video_port : bool):

        '''
            Paramaters:
                * resolution : tuple[int, int] : Specified stream quality. Particularly width and height of the frame.
                * framerate : int : Number of frames to be processed per second. 
                * content_type : str : String value for image type.
                * use_video_port : bool : True/False value whether or not the device should use its onboard video port or USB.
        '''
        
        self.resolution = resolution
        self.framerate = framerate
        self.content_type = content_type
        self.use_video_port = use_video_port
        self.object_detection = ObjectDetection(min_contour_area=650)
        self.annotations = Annotations()

    
    def generate_frames(self):

        with picamera2.Picamera2() as camera:
        
            configuration = camera.create_video_configuration(
                main={'size' : self.resolution}
            )

            camera.configure(configuration)
            camera.start()

            prev_frame = None

            try:

                while True:

                    frame = camera.capture_array()

                    if prev_frame is not None:

                        _, detection_bboxes = self.object_detection.detect_motion(prev_frame, frame)

                        if detection_bboxes:

                            annotated_frame = self.annotations.annotate_frame(frame, detection_bboxes)
                
                    prev_frame = frame

                    frame = cv2.cvtColor(annotated_frame, cv2.COLOR_RGB2BGR)

                    _, buffer = cv2.imencode('.jpg', frame)

                    frame_bytes = buffer.tobytes()

                    multipart_frame = (
                        b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
                    )

                    yield multipart_frame
            
            except GeneratorExit:
                print('Client has since disconnected. Stream halting!')
            
            finally:
                camera.stop()
