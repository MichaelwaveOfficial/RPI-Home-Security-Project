''' Ground truth file for single source of application configurations. '''

from dotenv import load_dotenv
from pathlib import Path 
import os 

load_dotenv()

''' Camera Settings.  '''

high_resolution = (1080, 720)
low_resolution = (640, 480)

high_frame_rate = 30
low_frame_rate = 20

content_type = 'jpeg'
use_video_port = True

''' Paths. '''

CAPTURES_DIR = 'captures'
BASE_DIR = Path(__file__).resolve().parent
CAMER_CONFIG = 'camera_settings.json'
CAMERA_CONFIG_PATH = os.path.join(BASE_DIR, CAMER_CONFIG)
CAPTURES_DIR_PATH = os.path.join(BASE_DIR, CAPTURES_DIR)

''' Base config file. '''

DEFAULT_SETTINGS = {
    "motion_detection" : {
        "sensitivity": 40,
        "threat_escalation_timer": 5,
        "maximum_threat_threshold": 3
    },
    "stream_quality" : {
        "preferred_quality": "performance",
        "performance": {
            "framerate": 20,
            "resolution": [
                640,
                480
            ]
        },
        "quality": {
            "framerate": 30,
            "resolution": [
                1080,
                720
            ]
        }
    },
    "alerts" : {
        "toggle": False,
        "frequency": 493
    },
    "client" : {
        "target_email": "example@email.com",
        "app_password": "password"
    }
}


''' Device Storage Configuration Settings. '''

FORMATTED_FILENAME_DATE : str = '%a-%b-%Y_%I-%M-%S%p'
FORMATTED_DISPLAY_DATE : str = '%I:%M:%S%p'
MAXIMUM_FILES_STORED : int = 60


''' EMAIL configs. '''

APP_EMAIL : str = os.getenv('APP_EMAIL')
APP_PASSWORD : str = os.getenv('APP_PASSWORD')
RECIPIENT_EMAIL : str = os.getenv('RECIPIENT_EMAIL')
