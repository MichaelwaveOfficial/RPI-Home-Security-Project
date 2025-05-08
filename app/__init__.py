from app.Routes import main 
from flask import Flask 
from .utils.device_utils.Camera import Camera
from app.utils.device_utils.ConfigManager import ConfigManager
from app.utils.device_utils.FileManager import FileManager
from .FrameProcessor import FrameProcessor
import os 
from app.settings import *


def build_app():

    app = Flask(__name__)

    app.file_manager = FileManager()
    app.config_manager = ConfigManager(config_file=CAMERA_CONFIG_PATH, default_config=DEFAULT_SETTINGS)

    # Instantiate Camera Object, apply settings.
    app.camera = Camera(
        resolution=high_resolution,
        framerate=high_frame_rate,
        content_type=content_type,
        use_video_port=use_video_port
    )

    @app.before_first_request
    def initalise_modules():
        app.camera.initialise_camera()
        app.frame_processor = FrameProcessor(app.camera)

    app.register_blueprint(main)
    
    # Return application.
    return app
    