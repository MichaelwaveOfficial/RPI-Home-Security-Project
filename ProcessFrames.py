import cv2
from utils.ObjectDetection import ObjectDetection
from utils.ObjectTracking import ObjectTracking
from utils.Camera import Camera
from utils.Annotate import Annotations
from settings import *

class ProcessFrames(object):
    
    def __init__(self):
        self.object_detection = ObjectDetection(min_contour_area=2500)
        self.annotations = Annotations()
        self.tracking = ObjectTracking()
        # Instantiate Camera Object, apply settings.
        self.camera = Camera(
            resolution=high_resolution,
            framerate=high_frame_rate,
            content_type=content_type,
            use_video_port=use_video_port
        )
        print('Intialised camera object.')

    
    def process_frames(self):

        prev_frame = None

        while True:

            frame = self.camera.read_frame()

            if prev_frame is not None:

                _, detection_bboxes = self.object_detection.detect_motion(prev_frame, frame)

                if detection_bboxes:

                    tracked_detections = self.tracking.update_tracker(detection_bboxes)

                    print(tracked_detections)

                    frame = self.annotations.annotate_frame(frame=frame, detections=tracked_detections)

                processed_frame_bytes = self.encode_frame_jpeg(frame)

                multipart_frame = (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + processed_frame_bytes + b'\r\n'
                )

                yield multipart_frame

    
    def encode_frame_jpeg(self, frame):

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        _, buffer = cv2.imencode('.jpg', frame)

        frame_bytes = buffer.tobytes()

        return frame_bytes
            