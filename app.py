import os
import io
import cv2
import time
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from importlib import import_module
from flask import Flask, render_template, Response, request, send_file
from multiprocessing import Pool
from rplidar import RPLidar
from PIL import Image

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'
lidar = RPLidar('/dev/ttyUSB0')

@app.route('/')
def index():
    lidar.stop()
    return render_template('index.html')

def gen_lidar():
    while True:
        for i, scan in enumerate(lidar.iter_scans(max_buf_meas=300, min_len=0)):
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
            ax.set_ylim([0, 900])
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


def lidar_read():
    frame = cv2.imread('lidar.jpg')
    ret, buffer = cv2.imencode('.jpg', frame)
    frame = buffer.tobytes()
    yield (b'--frame\r\n'
                b'Content-Type: image/jpg\r\n\r\n' + frame + b'\r\n')

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
    app.run(debug=True, host='172.20.10.2', port=5000)