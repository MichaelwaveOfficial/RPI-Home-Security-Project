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

    return render_template(
        'index.html'
    )


@app.route('/video_feed')
def video_feed():

    print(f'Is camera active : {camera.is_active()}?')

    if camera.is_active():
        return Response(
            frame_processor.generate_frames(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    else:
        return render_template(
            'camera_not_active.html',
        ), 503


if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True
    )