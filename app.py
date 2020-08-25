import os
import io
import cv2
import base64
import numpy as np
import matplotlib.pyplot as plt
from importlib import import_module
from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO
from flask_cors import CORS
from camera import Camera

from rplidar import RPLidar

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'
#lidar = RPLidar('/dev/ttyUSB0')

#camera_front = Camera(2)
#camera_left = Camera(0)
#camera_right = Camera(4)


@app.route('/')
def index():
    return render_template('index.html')

def gen_frames(camera_id):
    cap = cv2.VideoCapture(camera_id)  # capture the video from the live feed
    namelist = ['front', 'left', 'right']
    cap.set(3, 1920)
    cap.set(4, 1080)
    while True:
        success, frame = cap.read()  # read the camera frame
        cv2.imwrite('{}.jpg'.format(namelist[int(camera_id/2)]), frame)
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed_front')
def video_feed_front():
    return Response(gen_frames(0),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_right(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        decoded = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), -1)
        cv2.imwrite('right.jpg', decoded)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed_right')
def video_feed_right():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(4),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_left(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        decoded = cv2.imdecode(np.frombuffer(frame, dtype=np.uint8), -1)
        cv2.imwrite('left.jpg', decoded)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed_left')
def video_feed_left():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(2),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    front_name = request.form.get('Front')
    right_name = request.form.get('Right')
    left_name = request.form.get('Left')

    if front_name:
        os.rename('front.jpg', './front/' + front_name + '.jpg')
    if right_name:
        os.rename('right.jpg', './right/' + right_name + '.jpg')
    if left_name:
        os.rename('left.jpg', './left/' + left_name + '.jpg')
    
    return render_template('index.html')
    
def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    return base64.b64encode(img.getvalue())

def gen_lidar():
    while True:
        lidar.clear_input()
        for i, scan in enumerate(lidar.iter_scans(max_buf_meas=1000)):
            angle = []
            distance = []
            for data in scan:
                if data[2] > 1000:
                    pass
                else:
                    angle.append(data[1])
                    distance.append(data[2])
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='polar')
            c = ax.scatter(angle, distance, c=angle, s=20, cmap='hsv', alpha=0.75)
            plt.savefig('lidar.jpg')
            frame = cv2.imread('lidar.jpg')
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpg\r\n\r\n' + frame + b'\r\n')

@app.route('/lidar_feed')
def lidar_feed():
    return Response(gen_lidar(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True, host='192.168.50.23', port=5000)