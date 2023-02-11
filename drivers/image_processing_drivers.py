from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

from drivers.video_drivers import VideoStreamer

CAMERA_RESOLUTION = (640, 480)
CAMERA_FRAMERATE = 32

class ImageProcessor:
    def __init__(self, is_debug):
        self.is_debug = is_debug

        self.camera = PiCamera()
        self.camera.resolution = CAMERA_RESOLUTION
        self.camera.framerate = CAMERA_FRAMERATE
        self.raw_capture = PiRGBArray(self.camera, size = CAMERA_RESOLUTION)
        time.sleep(0.1)

        self.video_streamer = None

        if self.is_debug == True:
            self.video_streamer = VideoStreamer(port = 9999)
            self.video_streamer.connect()
            self.video_streamer.search_for_clients()

    def process_frame(self, frame):
        # Clear the stream
        self.raw_capture.truncate(0)

        # Frame Processing TBD
        processed_frame = None

        if self.is_debug:
            self.video_streamer.send_frame(bytes("Hello", encoding='utf-8'))

        return processed_frame

    def close(self):
        if self.is_debug:
            self.video_streamer.close()
        
        
