import os
import io
import cv2
import time
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
#import RPi.GPIO as gpio
from importlib import import_module
from flask import Flask, render_template, Response, request, send_file
from camera import CameraStream
from multiprocessing import Pool
from rplidar import RPLidar
from PIL import Image
import threading

app = Flask(__name__)
_pool = None
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'
#gpio.setwarnings(False)
#gpio.setmode(gpio.BOARD)

@app.route('/')
#@app.route('/<cmd>')
def index():

    return render_template('index.html')

def gen_frames_front():
    cap_front = CameraStream(4).start()  # capture the video from the live feed
    #cap.set(3, 1920)
    #cap.set(4, 1080)
    while True:
        frame = cap_front.read()  # read the camera frame
        cv2.imwrite('front.jpg', frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def gen_frames_right():
    cap_right = CameraStream(6).start()  # capture the video from the live feed
    #cap.set(3, 1920)
    #cap.set(4, 1080)
    while True:
        frame = cap_right.read()  # read the camera frame
        cv2.imwrite('right.jpg', frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

def gen_frames_left():
    cap_left = CameraStream(8).start()  # capture the video from the live feed
    #cap.set(3, 1920)
    #cap.set(4, 1080)
    while True:
        frame = cap_left.read()  # read the camera frame
        cv2.imwrite('left.jpg', frame)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video_feed_front')
def video_feed_front():
    #f = _pool.apply_async(gen_frames(4, 'front'))
    #r = f.get(timeout=2)
    return Response(gen_frames_front(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_right')
def video_feed_right():
    #f = _pool.apply_async(gen_frames(6, 'right'))
    #r = f.get(timeout=2)
    return Response(gen_frames_right(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed_left')
def video_feed_left():
    #f = _pool.apply_async(gen_frames(8, 'left'))
    #r = f.get(timeout=2)
    return Response(gen_frames_left(),
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
        lidar = RPLidar('/dev/ttyUSB1')
        for i, scan in enumerate(lidar.iter_scans(max_buf_meas=100, min_len=0)):
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
            ax.set_ylim([0, 1000])
            ax.set_theta_zero_location('N')
            ax.set_theta_direction(-1)
            ax.scatter(angle, distance, s=10, cmap='grey', alpha=0.75, vmin=0, vmax=1000)
            plt.savefig('lidar.jpg')
            plt.close(fig)
            frame = cv2.imread('lidar.jpg')
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpg\r\n\r\n' + frame + b'\r\n')

@app.route('/lidar_feed')
def lidar_feed():
    #f = _pool.apply_async(gen_lidar())
    #r = f.get(timeout=2)
    return Response(gen_lidar(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/lidar_save', methods=['POST'])
def lidar_save():
    name = request.form.get('Lidar')
    if name:
        os.rename('lidar_result.txt', './lidar/' + name + '.txt')
    return render_template('index.html')

if __name__ == "__main__":
    #_pool = Pool(processes=4)
    #try:
    
    app.run(debug=True, host='127.0.0.1', port=5000)
    #except KeyboardInterrupt:
        #_pool.close()
        #_pool.join()