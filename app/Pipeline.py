from .utils.device.Camera import Camera
from .utils.cv.Detection import ObjectDetection
from .utils.cv.Tracking import ObjectTracking
from .utils.cv.Annotation import Annotations

import cv2 

class SurveillancePipeline(object):

    ''' '''

    def __init__(self, resolution : int, framerate : tuple[int, int]):

        ''' '''

        self.resolution = resolution
        self.framerate = framerate

        self.camera = Camera(
            resolution=resolution,
            framerate=framerate,
        )

        self.detection = ObjectDetection(min_contour_area=2500)
        self.tracking = ObjectTracking()
        self.annotation = Annotations()
        self.prev_frame = None


    def generate_frames(self):

        ''' '''

        try:

            while True:

                frame = self.camera.read_frame()

                if self.prev_frame is not None:

                    _, detection_bboxes = self.detection.detect_motion(self.prev_frame, frame)

                    if detection_bboxes:

                        tracked_detections = self.tracking.update_tracker(detection_bboxes)

                        frame = self.annotation.annotate_frame(frame, tracked_detections)

                self.prev_frame = frame

                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                buffer = cv2.imencode('.jpg', frame)[1]

                frame_bytes = buffer.tobytes()

                multipart_frame = (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
                )

                yield multipart_frame

        except GeneratorExit:
            print('Client has disconnected. Stream halting.')
        finally:
            self.camera.halt()
