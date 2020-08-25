import os
import cv2
from base_camera import BaseCamera


class Camera(BaseCamera):

    def __init__(self, video_source):
        
        #if os.environ.get('OPENCV_CAMERA_SOURCE'):
        #    Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        #else:
        Camera.video_source = video_source
        super(Camera, self).__init__()

    #@staticmethod
    #def set_video_source(source):
    #    Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        print(Camera.video_source)
        print(camera)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        while True:
            # read current frame
            camera.set(3, 2921)
            camera.set(4, 2192) 
            _, img = camera.read()

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()