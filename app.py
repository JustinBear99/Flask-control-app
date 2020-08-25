import os
import io
import cv2
import base64
import numpy as np
import matplotlib.pyplot as plt
import RPi.GPIO as gpio
from importlib import import_module
from flask import Flask, render_template, Response, request, send_file
from flask_socketio import SocketIO
from flask_cors import CORS
from rplidar import RPLidar
from PIL import Image

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'
lidar = RPLidar('/dev/ttyUSB1')

gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)


@app.route('/')
@app.route('/<cmd>')
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

@app.route('/video_feed_right')
def video_feed_right():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(4),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

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
        for i, scan in enumerate(lidar.iter_scans(max_buf_meas=1000, min_len=0)):
            angle = []
            distance = []
            lidar_file = open('lidar_result.txt', 'w')
            lidar_file.writelines('Quality Angle(degree) Distance(mm)\n')
            for data in scan:
                if data[2] > 1000:
                    pass
                else:
                    angle.append(data[1]*np.pi/180)
                    distance.append(data[2])
                lidar_file.writelines(str(data[0]) + ' ' + str(data[1]) + ' ' + str(data[2]) + '\n')
            lidar_file.close()
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='polar')
            c = ax.scatter(angle, distance, s=10, cmap='grey', alpha=0.75, vmin=0, vmax=1000)
            ax.set_ylim([0, 1000])
            plt.savefig('lidar.jpg')
            plt.close(fig)
            frame = cv2.imread('lidar.jpg')
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpg\r\n\r\n' + frame + b'\r\n')

@app.route('/lidar_png')
def lidar_png():
    img = Image.open('A1-pic-left.png')
    
    return render_template('index.html', lidar_png=img)

@app.route('/lidar_feed')
def lidar_feed():
    return Response(gen_lidar(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/lidar_save', methods=['POST'])
def lidar_save():
    name = request.form.get('Lidar')
    if name:
        os.rename('lidar_result.txt', './lidar/' + name + '.txt')
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, host='192.168.50.23', port=5000)