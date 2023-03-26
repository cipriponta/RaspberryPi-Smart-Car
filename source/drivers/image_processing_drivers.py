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

        greyscale_frame, blurred_frame, thresholded_frame, contours = self.get_contours(frame)
        rectangle_outlines, lines = self.get_lines(contours)

        output_frame = None
        if IMAGE_OUTPUT_FRAME == IMAGE_OUTPUT.COLOR:
            output_frame = frame
        elif IMAGE_OUTPUT_FRAME == IMAGE_OUTPUT.GREYSCALE:
            output_frame = cv2.cvtColor(greyscale_frame, cv2.COLOR_GRAY2BGR)
        elif IMAGE_OUTPUT_FRAME == IMAGE_OUTPUT.BLURRED:
            output_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_GRAY2BGR)
        elif IMAGE_OUTPUT_FRAME == IMAGE_OUTPUT.THRESHOLDED:
            output_frame = cv2.cvtColor(thresholded_frame, cv2.COLOR_GRAY2BGR)
        
        processed_frame = self.draw_output(output_frame = output_frame,
                                            contours = contours,
                                            rectangle_outlines = rectangle_outlines,
                                            lines = lines)

        if self.is_debug:
            self.video_streamer.send_frame(processed_frame)

        return processed_frame

    def get_contours(self, frame):
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
        
        return greyscale_frame, blurred_frame, thresholded_frame, contours

    def get_lines(self, contours):
        lines_list = []
        rectangle_outlines = []

        for contour in contours:
            rectangle = cv2.minAreaRect(contour)
            rectangle_outline = numpy.int0(cv2.boxPoints(rectangle))
            rectangle_outlines.append(rectangle_outline)
            
            middle1 = numpy.array([int((rectangle_outline[0][0] + rectangle_outline[1][0]) / 2), 
                                   int((rectangle_outline[0][1] + rectangle_outline[1][1]) / 2)])
            middle2 = numpy.array([int((rectangle_outline[1][0] + rectangle_outline[2][0]) / 2), 
                                   int((rectangle_outline[1][1] + rectangle_outline[2][1]) / 2)])
            middle3 = numpy.array([int((rectangle_outline[2][0] + rectangle_outline[3][0]) / 2), 
                                   int((rectangle_outline[2][1] + rectangle_outline[3][1]) / 2)])
            middle4 = numpy.array([int((rectangle_outline[3][0] + rectangle_outline[0][0]) / 2), 
                                   int((rectangle_outline[3][1] + rectangle_outline[0][1]) / 2)])
            
            if numpy.linalg.norm(middle1 - middle3) > numpy.linalg.norm(middle2 - middle4):
                lines_list.append([middle1, middle3])
            else:
                lines_list.append([middle2, middle4])
           
        return rectangle_outlines, lines_list
    
    def draw_output(self, output_frame, contours, rectangle_outlines, lines):
        if IMAGE_DISPLAY_CONTOURS:
            cv2.drawContours(image = output_frame, 
                            contours = contours, 
                            contourIdx = -1, 
                            color = IMAGE_CONTOUR_COLOR, 
                            thickness = IMAGE_LINES_THICKNESS)
            
        if IMAGE_DISPLAY_BOUNDED_LINES:
            cv2.drawContours(image = output_frame, 
                            contours = rectangle_outlines, 
                            contourIdx = -1, 
                            color = IMAGE_RECTANGLE_COLOR, 
                            thickness = IMAGE_LINES_THICKNESS)

        if IMAGE_DISPLAY_LINES:
            for line in lines:
                cv2.line(img = output_frame,
                        pt1 = line[0],
                        pt2 = line[1],
                        color = IMAGE_LINES_COLOR,
                        thickness = IMAGE_LINES_THICKNESS)
        return output_frame

    def close(self):
        if self.is_debug:
            self.video_streamer.close()
        
        
