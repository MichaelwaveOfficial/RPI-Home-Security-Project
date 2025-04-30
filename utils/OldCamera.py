import io 
import picamera2
import cv2
from utils.ObjectDetection import ObjectDetection
from utils.ObjectTracking import ObjectTracking
from utils.Annotate import Annotations


class Camera(object):
    ''' Camera class to access and manipulate the devices onboard camera. '''

    def __init__(self, resolution: tuple[int, int], framerate: int, content_type: str, use_video_port: bool):
        self.resolution = resolution
        self.framerate = framerate
        self.content_type = content_type
        self.use_video_port = use_video_port
        self.object_detection = ObjectDetection(min_contour_area=2500)
        self.annotations = Annotations()
        self.tracking = ObjectTracking()
        
        # Initialize camera here to fail early if there's a problem
        try:
            self.camera = picamera2.Picamera2()
            config = self.camera.create_video_configuration(
                main={'size': self.resolution}
            )
            self.camera.configure(config)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize camera: {str(e)}")

    def generate_frames(self):
        try:
            self.camera.start()
            prev_frame = None

            while True:
                frame = self.camera.capture_array()

                if prev_frame is not None:
                    _, detection_bboxes = self.object_detection.detect_motion(prev_frame, frame)

                    if detection_bboxes:
                        tracked_detections = self.tracking.update_tracker(detection_bboxes)
                        print(tracked_detections)
                        frame = self.annotations.annotate_frame(frame=frame, detections=tracked_detections)
                
                prev_frame = frame
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        except GeneratorExit:
            print('Client has since disconnected. Stream halting!')
        finally:
            self.camera.stop()
            self.camera.close()

    def __del__(self):
        if hasattr(self, 'camera'):
            self.camera.stop()
            self.camera.close()