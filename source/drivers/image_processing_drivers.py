from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy
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

        # Frame Processing TBD
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_edges = cv2.Canny(image = frame_gray, 
                                threshold1 = IMAGE_EDGES_LOW_THRESHOLD, 
                                threshold2 = IMAGE_EDGES_HIGH_THRESHOLD, 
                                apertureSize = IMAGE_EDGES_APERTURE_SIZE)
        frame_road_lines = cv2.HoughLinesP(image = frame_edges, 
                                           rho = IMAGE_HOUGHLINES_RHO, 
                                           theta = IMAGE_HOUGHLINES_THETA, 
                                           threshold = IMAGE_HOUGHLINES_THRESHOLD, 
                                           minLineLength = IMAGE_HOUGHLINES_MIN_LINE_LENGTH, 
                                           maxLineGap = IMAGE_HOUGHLINES_MAX_LINE_GAP)

        if type(frame_road_lines) == numpy.ndarray:
            if frame_road_lines.size > 0:
                for road_line in frame_road_lines:
                    x1, y1, x2, y2 = road_line[0]
                    cv2.line(img = frame, 
                             pt1 = (x1, y1), 
                             pt2 = (x2, y2), 
                             color = IMAGE_HOUGHLINES_COLOR, 
                             thickness = IMAGE_HOUGHLINES_THICKNESS)

        processed_frame = frame

        if self.is_debug:
            self.video_streamer.send_frame(processed_frame)

        return processed_frame

    def close(self):
        if self.is_debug:
            self.video_streamer.close()
        
        
