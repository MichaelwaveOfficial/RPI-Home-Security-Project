''' Basic web server leveraging Flask web framework where video is streamed from the raspberry pis camera. '''

from flask import Flask, Response, render_template
from camera import Camera
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


@app.route('/')
def index():

    return render_template(
        'index.html'
    )


@app.route('/video_feed')
def video_feed():
    return Response(
        camera.generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
