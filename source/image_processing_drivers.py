from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

class ImageProcessor:
    def __init__(self):
        self.camera = PiCamera()
        self.capture = PiRGBArray(self.camera)
        time.sleep(0.1)

    def return_frame(self):
        self.camera.capture(self.capture, format = "bgr")
        return self.capture.array
