''' Basic web server leveraging Flask web framework where video is streamed from the raspberry pis camera. '''

from flask import Flask, Response, render_template, request, jsonify, send_from_directory
from utils.Camera import Camera
from FrameProcessor import FrameProcessor
from settings import *
from utils.ConfigManager import ConfigManager
from utils.FileManager import FileManager
import re
import time 

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

    camera_active = camera.is_active()

    return render_template(
        'index.html',
        camera_active=camera_active
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


@app.route('/captures/<path:filename>')
def serve_capture_file(filename):
    # serves GET /captures/<filename>
    return send_from_directory(CAPTURES_DIR, filename)


@app.route('/captures', methods=['GET'])
def captures():

    sort_order = request.args.get('sort', 'newest')

    file_manager.file_order = (sort_order == 'oldest')

    filename = request.args.get('filename')
    images = file_manager.access_stored_captures(CAPTURES_DIR)
    current_image = file_manager.serve_file(filename, CAPTURES_DIR) if filename else None

    return render_template(
        'captures.html',
        images=images,
        current_image=current_image,
        sort_order=sort_order
    )


@app.route('/captures/delete/<path:filename>', methods=['POST'])
def delete_capture(filename):

    file_path = os.path.join(CAPTURES_DIR, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted: {file_path}")
    else:
        print(f"File not found: {file_path}")

    return redirect(url_for('captures'))


@app.route('/status')
def device_status():

    formatted_uptime = time.strftime('%H:%M:%S', time.gmtime(time.time() - camera.uptime)) if camera.uptime else "Inactive"

    captures_today = file_manager.serve_captures_today(CAPTURES_DIR)

    camera_status = {
        'status' : camera.is_active(),
        'uptime' : formatted_uptime,
        'caps_today' : len(captures_today)
    }

    return render_template(
        'status.html',
        camera_status=camera_status
    ) 


if __name__ == '__main__':

    # Application entry point.

    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True
    )