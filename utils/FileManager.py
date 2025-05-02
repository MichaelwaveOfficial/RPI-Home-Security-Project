import os 

class FileManager(object):

    def __init__(self):

        # Store value of the file order when displaying captures stored on screen.
        self.file_order : bool = False


    def sort_files(self, files : list[dict], reverse_order : bool = False) -> list[dict]:

        '''
        Sort list containing captures from newest to oldest from the order parameterised, OS natively sorts in order due to filenames date+time structure,
        meaning it is simple enough to reverse the list these entries are stored in. 

        :param: files - list of files to be sorted. 
        :param: reverse_order - Order required for files to be sorted into.
        :return: sorted_list - Sorted list of images.
        '''

        return sorted(
            files,
            key=lambda cap: f"{cap['capture_date']}{cap['capture_time']}",
            reverse=reverse_order
        )
    

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

        # Does not want to create the specific directory because Linux...

        if not os.path.exists(directory):
            os.makedirs(directory)

        # Loop over all image files found within the captures directory. 
        for file in os.listdir(directory):

    
            # Check the file extensions match those desired.
            if file.endswith(('.jpg', '.jpeg', '.png')):

                # Append the filename to the captures directory path.
                fullpath = os.path.join(directory, file)
                # Get the standalone filename (date) and the file extention.
                filename, file_ext = os.path.splitext(file)
                # Access just the date.
                capture_date = filename.split('_')[0]
                # Access the time. 
                capture_time = filename.split('_')[1]

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
                })

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
