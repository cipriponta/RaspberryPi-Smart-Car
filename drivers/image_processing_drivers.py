from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

from drivers.video_drivers import VideoStreamer

CAMERA_RESOLUTION = (320, 240)
CAMERA_FRAMERATE = 120
CAMERA_SHUTTER_SPEED = 20000
CAMERA_ISO = 800

class ImageProcessor:
    def __init__(self, is_debug):
        self.is_debug = is_debug

        self.camera = PiCamera()
        self.camera.shutter_speed = CAMERA_SHUTTER_SPEED
        self.camera.iso = CAMERA_ISO
        print("Exposure speed: ", self.camera.exposure_speed)
        print("Shutter speed: ", self.camera.shutter_speed)
        self.camera.resolution = CAMERA_RESOLUTION
        self.camera.framerate = CAMERA_FRAMERATE
        self.raw_capture = PiRGBArray(self.camera, size = CAMERA_RESOLUTION)
        time.sleep(0.1)

        self.video_streamer = None

        if self.is_debug == True:
            self.video_streamer = VideoStreamer(port = 9999)
            self.video_streamer.connect()
            self.video_streamer.search_for_clients()

    def get_processed_frame(self):
        self.camera.capture(self.raw_capture, format="bgr")
        frame = self.raw_capture.array
        
        # Clear the stream
        self.raw_capture.truncate(0)

        # Frame Processing TBD
        processed_frame = frame

        if self.is_debug:
            self.video_streamer.send_frame(processed_frame)

        return processed_frame

    def close(self):
        if self.is_debug:
            self.video_streamer.close()
        
        
