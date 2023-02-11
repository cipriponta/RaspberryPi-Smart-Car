from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

CAMERA_RESOLUTION = (640, 480)
CAMERA_FRAMERATE = 10

class ImageProcessor:
    def __init__(self):
        self.camera = PiCamera()
        self.camera.resolution = CAMERA_RESOLUTION
        self.camera.framerate = CAMERA_FRAMERATE
        self.capture = PiRGBArray(self.camera)
        time.sleep(0.1)

    def return_frame(self):
        self.camera.capture(self.capture, format = "bgr")
        return self.capture.array
