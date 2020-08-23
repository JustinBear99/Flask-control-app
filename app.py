import os
import cv2
import numpy as np
from importlib import import_module
from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO
from flask_cors import CORS

if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        decoded = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), -1)
        cv2.imwrite('123.jpg', decoded)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/captureframe', methods=['POST'])
def captureframe():
    #currentFrame = Camera().get_frame()
    name = request.form.get('Name')
    return render_template('index.html', name=name)
    


if __name__ == "__main__":
    app.run(debug=True, host='192.168.50.23', port=5000)