
from flask import Flask, Response, render_template, request, jsonify, send_from_directory, Blueprint, current_app
from .settings import *
import re
import time 

# Register main app blueprint.
main = Blueprint('main', __name__)

@main.route('/')
def index():

    camera = current_app.camera

    ''' Application main page. '''

    camera_active = camera.is_active()

    return render_template(
        'index.html',
        camera_active=camera_active
    )


@main.route('/video_feed')
def video_feed():

    camera = current_app.camera

    ''' Route to render the cameras captured frames. '''

    # If camera status is active.
    if camera.is_active():

        # Return generator function response with cameras frames.
        return Response(
            current_app.frame_processor.generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    else:

        # Otherwise, inform users camera is currently inactive.
        return render_template(
            'camera_not_active.html'
        ), 503


@main.route('/settings')
def settings():

    config_manager = current_app.config_manager

    ''' Render settings paeg with current camera configuration. '''

    settings = config_manager.load_settings() 

    return render_template(
        'settings.html',
        settings=settings
    )


@main.route('/settings/update', methods=['POST'])
def update_settings():

    ''' Update camera settings based on user form input. '''

    try:

        config_manager = current_app.config_manager

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


@main.route('/captures/<path:filename>')
def serve_capture_file(filename):
    # serves GET /captures/<filename>
    return send_from_directory(CAPTURES_DIR_PATH, filename)


@main.route('/captures', methods=['GET'])
def captures():

    file_manager = current_app.file_manager

    sort_order = request.args.get('sort', 'newest')

    file_manager.file_order = (sort_order == 'oldest')

    filename = request.args.get('filename')
    images = file_manager.access_stored_captures(CAPTURES_DIR_PATH)
    current_image = file_manager.serve_file(filename, CAPTURES_DIR_PATH) if filename else None

    return render_template(
        'captures.html',
        images=images,
        current_image=current_image,
        sort_order=sort_order
    )


@main.route('/captures/delete/<path:filename>', methods=['POST'])
def delete_capture(filename):

    file_path = os.path.join(CAPTURES_DIR_PATH, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted: {file_path}")
    else:
        print(f"File not found: {file_path}")

    return redirect(url_for('captures'))


@main.route('/status')
def device_status():

    camera = current_app.camera
    file_manager = current_app.file_manager

    formatted_uptime = time.strftime('%H:%M:%S', time.gmtime(time.time() - camera.uptime)) if camera.uptime else "Inactive"

    captures_today = file_manager.serve_captures_today(CAPTURES_DIR_PATH)

    camera_status = {
        'status' : camera.is_active(),
        'uptime' : formatted_uptime,
        'caps_today' : len(captures_today)
    }

    return render_template(
        'status.html',
        camera_status=camera_status
    ) 
    