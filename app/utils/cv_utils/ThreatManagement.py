import cv2
import yagmail 
import os 
from datetime import datetime 
import time 
from ...settings import *


class ThreatManagement(object):

    def __init__(
            self,
            CLIENT_USERNAME : str,
            CLIENT_PASSWORD : str,
            TARGET_EMAIL : str, 
            MAX_THREAT_LEVEL : int,
            CAPTURES_DIR : str
        ):

        self.CLIENT_USERNAME = CLIENT_USERNAME
        self.CLIENT_PASSWORD = CLIENT_PASSWORD
        self.TARGET_EMAIL = TARGET_EMAIL
        self.MAX_THREAT_LEVEL = MAX_THREAT_LEVEL
        self.CAPTURES_DIR = CAPTURES_DIR
        
        if not os.path.exists(self.CAPTURES_DIR):
            os.makedirs(self.CAPTURES_DIR)

        self.yagmail_client = yagmail.SMTP(self.CLIENT_USERNAME, self.CLIENT_PASSWORD)

        self.handled_IDs = set()


    def handle_threats(self, tracked_detections, frame):

        ''' Iterate over detections being tracked and assess their threat level. '''

        for detection in tracked_detections:
            self.check_threat_level(detection, frame) 

    
    def check_threat_level(self, detection, frame):

        ID = detection.get('ID')

        if detection['threat_level'] >= self.MAX_THREAT_LEVEL and \
            ID not in self.handled_IDs:

            print('Detection has exceeded maximum threat level, handling accordingly.')

            full_path = self.capture_frame(frame, ID)

            self.send_email_alert(detection, full_path)

            self.handled_IDs.add(ID)


    def capture_frame(self, frame, ID):

        timestamp = datetime.now().strftime(FORMATTED_FILENAME_DATE)

        capture_filename = f'detection_{ID}_{timestamp}.jpg'
        
        fullpath = os.path.join(self.CAPTURES_DIR, capture_filename)

        success = cv2.imwrite(fullpath, frame)

        if not success:
            raise IOError(f'Failed to write image to {fullpath}')

        print("Saving to:", CAPTURES_DIR_PATH)

        return fullpath

    
    def send_email_alert(self, detection, fullpath, max_retries : int = 3, secs_delay : int = 10) -> None:

        ''' 
            Uses envinronment variables to send an email from a given gmail account to the users recipient address with an alert
                encapsulating data about the detection and the media where it has been captured.

            Paramaters:
                * media (np.ndarray | mp4 video) : Parsed media wether it is a single frame acting as a still image 
                    or a processed mp4 video of the event. 
                * max_retries (int) : Number of tries before operation is terminated. 
                * secs_delay (int) : Number of seconds until an attempt to resend the email if unsuccessful is made. 

            Returns:
                * None : Returns early if operation successful. 
        '''

        if not os.path.exists(fullpath):
            raise FileNotFoundError(f"Capture not found at {fullpath}")

        # Make an attempt until max retries threshold met.
        for attempt in range(max_retries + 1):

            try:

                # Email subject. 
                subject = f'Security Alert: Threat detected at level {detection["threat_level"]}'

                # Email contents.
                contents = f'''
                    Detected at: {time.strftime("%Y-%m-%d %H:%M:%S")}\n
                    Please see the capture attatched. 
                '''

                # Email object.
                self.yagmail_client.send(
                    to=self.TARGET_EMAIL,
                    subject=subject, 
                    contents=contents,
                    attachments=fullpath
                )

                # Return early if successful.
                return

            except (yagmail.YagConnectionClosed, yagmail.YagAddressError):
                
                # If max tries met, raise error with user.
                if attempt == max_retries:
                    raise RuntimeError(f'Failed to send email alert after {max_retries} attempts.')
                
                # Delay next attempt.
                time.sleep(secs_delay)

    
    def clean_set_IDs(self, persistence_timer : int = 600):

        ''' Free up resources if values handled exceed their expiry. '''

        current_time = time.time()

        expired_IDs = [
            ID for ID, time in self.handled_IDs.items() if current_time - time > persistence_timer
        ]

        for ID in expired_IDs:
            del self.handled_IDs[ID]
