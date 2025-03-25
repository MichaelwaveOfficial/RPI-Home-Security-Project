from flask import Blueprint, Response, render_template
from .utils.device.Camera import Camera
from app.Settings import *


# Register main app blueprint.
main = Blueprint('main', __name__)

# Instantiate Camera Object, apply settings.
camera = Camera(
    resolution=high_resolution,
    framerate=high_frame_rate,
    content_type=content_type,
    use_video_port=use_video_port
)


@main.route('/')
def index():

    return render_template(
        'index.html'
    )


@main.route('/video_feed')
def video_feed():

    ''' Route leveraging a generator function to stream captured video frames to the client. '''

    return Response(
        camera.generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@main.route('/settings')
def settings():

    ''' Render settings page with current camera configuration. '''

    render_template(
        'settings.html'
    )


@main.route('/settings/update', methods=['POST'])
def update_settings():

    ''' Update camera settings based on user form input. '''



@main.route('/captures')
def captures():

    ''' Render captures page with a list of images stored on the device. '''

    return render_template(
        'captures.html',
        images=[], # Accumulate list of images on device
        image=None # USer selected image.
    )