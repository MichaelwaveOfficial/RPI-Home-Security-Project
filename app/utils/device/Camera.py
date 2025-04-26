
from picamera2 import Picamera2

class Camera(object):

    ''' Camera class to access and manipulate the devices onboard camera. '''

    def __init__(self, resolution : tuple[int, int], framerate : int):

        '''
            Paramaters:
                * resolution : tuple[int, int] : Specified stream quality. Particularly width and height of the frame.
                * framerate : int : Number of frames to be processed per second. 
        '''

        self.resolution = resolution
        self.framerate = framerate
        self.camera = Picamera2()
        self.configuration = self.camera.create_video_configuration(
            main={
                'size' : resolution
            }
        )
        self.camera.configure(self.configuration)
        self.camera.set_controls({'FrameRate' : self.framerate})
        self.camera.start()
        

    def read_frame(self):

        ''' Capture frame from onboard camera. '''

        try:

            frame = self.camera.capture_array()

            if frame is None:
                raise RuntimeError('Failed to capture frame: capture_array() method returned None.')

            return frame 
            
        except Exception as e:
            raise RuntimeError(f'Error reading frame from devices onboard camera: {e}')

        return self.camera.capture_array()

    
    def halt(self):

        ''' Close camera for resource cleanup. ''' 

        self.camera.stop()
        self.camera.close()
