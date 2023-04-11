from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from drivers.video_drivers import VideoStreamer
from constants import *

class Point:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.coords = numpy.array([self.width, self.height])

    def __repr__(self):
        return f"({self.width}, {self.height})"
    
    def crop(self):
        if self.width < 0:
            self.width = 0
        elif self.width > CAMERA_IMAGE_WIDTH:
            self.width = CAMERA_IMAGE_WIDTH

        if self.height < 0:
            self.height = 0
        elif self.height > CAMERA_IMAGE_HEIGHT:
            self.height = CAMERA_IMAGE_HEIGHT

class Line:
    def __init__(self, pt1, pt2):
        self.origin = None
        self.tip = None

        # Comparing line heights to find out which point is the tip 
        # and which point is the origin
        if pt1.height > pt2.height:
            self.origin = pt1
            self.tip = pt2
        else:
            self.origin = pt2
            self.tip = pt1

        self.length = numpy.linalg.norm(self.origin.coords - self.tip.coords)
    
    def __repr__(self):
        return f"[O: {self.origin}, T: {self.tip}, L: {self.length}]"
    
    def check_min_line_length(self):
        if self.length > IMAGE_LINES_MIN_LENGTH:
            return True
        else:
            return False

    def draw(self, output_image):
        cv2.arrowedLine(img = output_image,
                        pt1 = self.origin.coords,
                        pt2 = self.tip.coords,
                        color = IMAGE_LINES_COLOR,
                        thickness =  IMAGE_LINES_THICKNESS)
        
class ProcessedContour:
    def __init__(self, contour):
        self.contour = contour
        self.rectangle = cv2.minAreaRect(self.contour)
        self.rectangle_outline = numpy.int0(cv2.boxPoints(self.rectangle))

    def draw(self, output_frame):
        if IMAGE_DISPLAY_CONTOURS:
            cv2.drawContours(image = output_frame, 
                             contours = [self.contour], 
                             contourIdx = 0, 
                             color = IMAGE_CONTOUR_COLOR, 
                             thickness = IMAGE_LINES_THICKNESS)
            
        if IMAGE_DISPLAY_BOUNDED_LINES:
            cv2.drawContours(image = output_frame, 
                             contours = [self.rectangle_outline], 
                             contourIdx = 0, 
                             color = IMAGE_RECTANGLE_COLOR, 
                             thickness = IMAGE_LINES_THICKNESS)

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

        self.frame = None
        self.greyscale_frame = None
        self.blurred_frame = None
        self.thresholded_frame = None
        self.output_frame = None

        self.contours = None
        self.processed_contours = []

    def get_line_shift(self):
        self.camera.capture(self.raw_capture, format = IMAGE_FORMAT_BGR)
        self.frame = self.raw_capture.array
        
        # Clear the stream
        self.raw_capture.truncate(0)

        self.get_contours()

        if self.is_debug:
            if IMAGE_OUTPUT_FRAME == IMAGE_OUTPUT.COLOR:
                self.output_frame = self.frame
            elif IMAGE_OUTPUT_FRAME == IMAGE_OUTPUT.GREYSCALE:
                self.output_frame = cv2.cvtColor(self.greyscale_frame, cv2.COLOR_GRAY2BGR)
            elif IMAGE_OUTPUT_FRAME == IMAGE_OUTPUT.BLURRED:
                self.output_frame = cv2.cvtColor(self.blurred_frame, cv2.COLOR_GRAY2BGR)
            elif IMAGE_OUTPUT_FRAME == IMAGE_OUTPUT.THRESHOLDED:
                self.output_frame = cv2.cvtColor(self.thresholded_frame, cv2.COLOR_GRAY2BGR)

            self.draw(self.output_frame)
            self.video_streamer.send_frame(self.output_frame)

        return 0

    def get_contours(self):
        self.greyscale_frame = cv2.cvtColor(src = self.frame, 
                                            code = cv2.COLOR_BGR2GRAY)
        self.blurred_frame = IMAGE_THRESHOLD_BLUR_METHOD(src =  self.greyscale_frame,
                                                         ksize = (IMAGE_THRESHOLD_BLOCK_SIZE, IMAGE_THRESHOLD_BLOCK_SIZE),
                                                         sigmaX = IMAGE_THRESHOLD_SIGMA_X)
        self.thresholded_frame = cv2.adaptiveThreshold(src = self.blurred_frame,
                                                       maxValue = IMAGE_GREYSCALE_MAX_VALUE,
                                                       adaptiveMethod = IMAGE_THRESHOLD_ADAPTIVE_METHOD,
                                                       thresholdType = IMAGE_THRESHOLD_TYPE,
                                                       blockSize = IMAGE_THRESHOLD_BLOCK_SIZE,
                                                       C = IMAGE_THRESHOLD_SUBTRACTED_CONSTANT)
        self.contours, _ = cv2.findContours(image = self.thresholded_frame,
                                            mode = IMAGE_CONTOUR_RETRIEVAL_MODE,
                                            method = IMAGE_CONTOUR_APPROX_METHOD)
        
        self.processed_contours.clear()
        for contour in self.contours:
            self.processed_contours.append(ProcessedContour(contour))  
    

    def draw(self, output_frame):
        for contour in self.processed_contours:
            contour.draw(output_frame)

    def close(self):
        if self.is_debug:
            self.video_streamer.close()
        
        
