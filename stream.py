''' Basic web server leveraging Flask web framework where video is streamed from the raspberry pis camera. '''

from flask import Flask, Response, render_template
from utils.Camera import Camera
from FrameProcessor import FrameProcessor
from settings import *

# Instantiate Flask application.
app = Flask(__name__)

# Instantiate Camera Object, apply settings.
camera = Camera(
    resolution=high_resolution,
    framerate=high_frame_rate,
    content_type=content_type,
    use_video_port=use_video_port
)

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
            'camera_not_active.html',
        ), 503


''' Other additional routes for later implementation. '''


@app.route('/settings')
def settings():
    pass 


@app.route('/captures')
def captures():
    pass 


@app.route('/device_status')
def device_status():
    pass 


if __name__ == '__main__':

    # Application entry point.

    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True
    )