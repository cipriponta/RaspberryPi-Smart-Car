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
        self.camera.rotation = CAMERA_ROTATION

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
        greyscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred_frame = IMAGE_THRESHOLD_BLUR_METHOD(src =  greyscale_frame,
                                                    ksize = (IMAGE_THRESHOLD_BLOCK_SIZE, IMAGE_THRESHOLD_BLOCK_SIZE),
                                                    sigmaX = IMAGE_THRESHOLD_SIGMA_X)
        thresholded_frame = cv2.adaptiveThreshold(src = blurred_frame,
                                                  maxValue = IMAGE_GREYSCALE_MAX_VALUE,
                                                  adaptiveMethod = IMAGE_THRESHOLD_ADAPTIVE_METHOD,
                                                  thresholdType = IMAGE_THRESHOLD_TYPE,
                                                  blockSize = IMAGE_THRESHOLD_BLOCK_SIZE,
                                                  C = IMAGE_THRESHOLD_SUBTRACTED_CONSTANT)
        contours, hierarchy = cv2.findContours(image = thresholded_frame,
                                               mode = IMAGE_CONTOUR_RETRIEVAL_MODE,
                                               method = IMAGE_CONTOUR_APPROX_METHOD)             

        output_frame = cv2.cvtColor(thresholded_frame, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(image = output_frame,
                         contours = contours,
                         contourIdx = -1, 
                         color = IMAGE_LINES_COLOR,
                         thickness = IMAGE_LINES_THICKNESS)
        
        rectangle_list = []
        for contour in contours:
            rectangle = cv2.minAreaRect(contour)
            rectangle_outline = numpy.int0(cv2.boxPoints(rectangle))
            print(rectangle_outline)
            try:
                cv2.drawContours(output_frame, [rectangle_outline], 0, (0, 0, 255), 1)
            except Exception as e:
                print(e)
        
        return output_frame

    def close(self):
        if self.is_debug:
            self.video_streamer.close()
        
        
