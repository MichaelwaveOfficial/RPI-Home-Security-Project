
import picamera2
import cv2


class Camera(object):

    ''' 
        Camera class to access and manipulate the devices onboard camera. Hopefully, SRP ++ extensibility will make this 
        easier to handle simultaneous cameras. 
    '''

    def __init__(self, resolution: tuple[int, int], framerate: int, content_type: str, use_video_port: bool):

        '''
            resolution: tuple(int, int) - The resolution of the captured video.
            framerate: int - Frame rate for the video stream.
            content_type: str - Type of content (unused currently, placeholder for future use).
            use_video_port: bool - Whether to use the video port (for speed).
        '''

        self.resolution = resolution
        self.framerate = framerate
        self.content_type = content_type
        self.use_video_port = use_video_port
        self.camera = None

        # Initialise camera in constructor when object is called. 
        self.initialise_camera()
        print(">>> Camera object:", self.camera)
        print(">>> is_active() →", self.is_active())


    
    def is_active(self):

        # Camera class status.
        return self.camera is not None

    
    def initialise_camera(self):

        ''' Method to initialise camera with set configurations.'''
       
        try:
            self.camera = picamera2.Picamera2()
            config = self.camera.create_preview_configuration(
                main={'size': self.resolution}
            )
            self.camera.configure(config)
            self.camera.start()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize camera: {str(e)}")
        

    def read_frame(self):

        ''' Capture frame from devices onboard camera. '''

        if not self.camera:
            raise RuntimeError('Camera not yet initialised.')

        try:

            frame = self.camera.capture_array()

            return frame 

        except Exception as e:
            print(f'Client has since disconnected. Stream halting!\n\n{e}')
 

    def close_camera(self):
        
        ''' Close camera as demonstrated in Picamera2 docs. '''

        if self.camera:
            self.camera.stop()
            self.camera.close()
            self.camera = None

    
    def __del__(self):

        ''' Destructor method to ensure camera object is destroyed. '''

        self.close_camera()
