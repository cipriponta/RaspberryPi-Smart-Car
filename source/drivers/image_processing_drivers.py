from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from drivers.video_drivers import VideoStreamer
from constants import *

class ImageProcessor:
    def __init__(self, is_debug):
        self.is_debug = is_debug

        self.camera = PiCamera()
        self.camera.shutter_speed = CAMERA_SHUTTER_SPEED
        self.camera.iso = CAMERA_ISO
        self.camera.resolution = CAMERA_RESOLUTION
        self.camera.framerate = CAMERA_FRAMERATE

        self.raw_capture = PiRGBArray(self.camera, size = CAMERA_RESOLUTION)
        time.sleep(CAMERA_INIT_TIME)

        self.video_streamer = None

        if self.is_debug == True:
            self.video_streamer = VideoStreamer(port = RPI_PORT)
            self.video_streamer.connect()
            self.video_streamer.search_for_clients()

    def get_processed_frame(self):
        self.camera.capture(self.raw_capture, format = IMAGE_FORMAT_BGR)
        frame = self.raw_capture.array
        
        # Clear the stream
        self.raw_capture.truncate(0)

        processed_frame = self.get_lines(frame)

        if self.is_debug:
            self.video_streamer.send_frame(processed_frame)

        return processed_frame

    def get_lines(self, frame):
        frame_grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        threshold_ret_value, thresholded_frame = cv2.threshold(src = frame_grayscale,
                                                               thresh = IMAGE_GREYSCALE_THRESHOLD_VALUE,
                                                               maxval = IMAGE_GREYSCALE_MAX_VALUE,
                                                               type = cv2.THRESH_BINARY_INV)
        contours, hierarchy = cv2.findContours(image = thresholded_frame,
                                               mode = cv2.RETR_LIST,
                                               method = cv2.CHAIN_APPROX_SIMPLE) 
        print(contours)
        output_frame = cv2.cvtColor(thresholded_frame, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(image = output_frame,
                         contours = contours,
                         contourIdx = -1, 
                         color = IMAGE_LINES_COLOR,
                         thickness = IMAGE_LINES_THICKNESS)
        
        return output_frame

    def close(self):
        if self.is_debug:
            self.video_streamer.close()
        
        
