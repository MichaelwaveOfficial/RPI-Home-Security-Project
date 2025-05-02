''' Basic web server leveraging Flask web framework where video is streamed from the raspberry pis camera. '''

from flask import Flask, Response, render_template, request, jsonify
from utils.Camera import Camera
from FrameProcessor import FrameProcessor
from settings import *
from utils.ConfigManager import ConfigManager
from utils.FileManager import FileManager
import re

# Instantiate Flask application.
app = Flask(__name__)

# Instantiate Camera Object, apply settings.
camera = Camera(
    resolution=high_resolution,
    framerate=high_frame_rate,
    content_type=content_type,
    use_video_port=use_video_port
)

file_manager = FileManager()
config_manager = ConfigManager(config_file=CAMERA_CONFIG_PATH, default_config=DEFAULT_SETTINGS)
frame_processor = FrameProcessor(camera)

@app.route('/')
def index():

    ''' Application main page. '''

    return render_template(
        'index.html'
    )


@app.route('/video_feed')
def video_feed():

    ''' Route to render the cameras captured frames. '''

    # If camera status is active.
    if camera.is_active():

        # Return generator function response with cameras frames.
        return Response(
            frame_processor.generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    else:

        # Otherwise, inform users camera is currently inactive.
        return render_template(
            'camera_not_active.html'
        ), 503


''' Other additional routes for later implementation. '''


@app.route('/settings')
def settings():

    ''' Render settings paeg with current camera configuration. '''

    settings = config_manager.load_settings() 

    return render_template(
        'settings.html',
        settings=settings
    )


@app.route('/settings/update', methods=['POST'])
def update_settings():

    ''' Update camera settings based on user form input. '''

    try:

        ''' 1) Persist incoming data to JSON. '''

        for key, updated_value in request.form.items():

            keys = re.findall(r'\w+', key)

            config_manager.update_settings(keys, updated_value)

        ''' 2) Load settings with updated values. '''

        settings = config_manager.load_settings() 

        ''' 3) Push values into frameprocessor where all modules are initialised. '''
        frame_processor.update_modules_settings(settings)

        # Return JSON success response. 
        return jsonify({"status": "success", "message": "Settings updated successfully"})
    
    except ValueError as e:
        # Return JSON error response. 
        return jsonify({"status": "error", "message": f"Failed to update settings!\n{e}"})


@app.route('/captures')
def captures():

    filename = request.args.get('filename')
    images = file_manager.access_stored_captures(CAPTURES_DIR)

    image = file_manager.serve_file(filename, CAPTURES_DIR) if filename else None
    
    return render_template(
        'captures.html',
        images=images,
        image=image
    ) 


@app.route('/status')
def device_status():

    return render_template(
        'status.html'
    ) 


if __name__ == '__main__':

    # Application entry point.

    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True
    )