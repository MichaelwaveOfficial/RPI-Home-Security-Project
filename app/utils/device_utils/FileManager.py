import os 
from datetime import datetime
import time
from app.settings import CAPTURES_DIR


class FileManager(object):

    def __init__(self):

        # Store value of the file order when displaying captures stored on screen.
        self.file_order : bool = False


    def access_stored_captures(self, directory: str) -> list[dict[str, str]]:

        '''
        Access images stored locally on the device. By iterating over each file, it will accumulate the meta data associated
        with each image, appending it to a dictionary, forming the metadata for an image which can be rendered into a html template,
        sanitised which can provide useful output for the user. 

        :params: directory - Access the cameras capture directory attribute.
        :return: stored_images - list consisting of dictionaries containing an images metadata for later access. 
        (img = {'fullpath','filename','file_ext', 'capture_date'})
        '''

        files = []

        # Loop over all image files found within the captures directory. 
        for file in os.listdir(directory):

    
            # Check the file extensions match those desired.
            if file.endswith(('.jpg', '.jpeg', '.png')):

                # Append the filename to the captures directory path.
                fullpath = os.path.join(directory, file)
                # Get the standalone filename (date) and the file extention.
                filename, file_ext = os.path.splitext(file)
            
                filename_parts = filename.split('_')

                ID = filename_parts[1]
                capture_date = filename_parts[2]
                capture_time = filename_parts[3]

                # Append the images data to the images dictionary. 
                files.append({
                    # Full filepath.
                    'fullpath': fullpath,
                    # Standalone filename.
                    'filename': filename,
                    # Files extension.
                    'file_ext': file_ext,
                    # Date it was captured.
                    'capture_date': capture_date, 
                    # Time the capture was taken.
                    'capture_time' : capture_time,
                    # Detection ID
                    'ID' : ID
                })

        # Sort the files based on capture_date and capture_time
        files.sort(key=lambda x: (x['capture_date'], x['capture_time']), reverse=not self.file_order)

        # Return dictionary containing meta data associated with images.
        return files
    

    def check_file_exhaustion(self, directory : str, file_limit : int) -> None:

        '''
            Check stored files, remove oldest captures in order to mitigate resource exhaustion, can be set by user. 

            :param: directory - Specified directory where files are stored. 
            :param: file_limit - Maximum number of files allowed within the devices local storage. 
            :return: N/A.
        '''

        try:

            files = sorted(os.listdir(directory), key=os.path.getmtime)

            for file in files[file_limit:]:
                fullpath = os.path.join(directory, file)
                os.remove(fullpath)
                print(f'Storage limits exceeded!\n {fullpath} has been deleted from the system to mitigate resource exhausiton!')

        except FileNotFoundError:
            print(f'Directory : {directory} not found!')

        
    def serve_file(self, filename : str, directory : str):

        '''
            Serve specific image from parsed filename.

            filename
            directory
        '''

        files = self.access_stored_captures(directory)
        
        for img in files:

            if img['filename'] == filename:
                return img

        return None

    
    def serve_captures_today(self, directory):

        captures_today = []
        
        today_str = datetime.now().strftime('%Y-%m-%d')

        all_captures = self.access_stored_captures(CAPTURES_DIR)

        for cap in all_captures:

            filename = cap['filename']

            if today_str in filename:
                captures_today.append(cap)

        return captures_today
