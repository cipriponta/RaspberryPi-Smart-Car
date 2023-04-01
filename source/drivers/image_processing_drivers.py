from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
from drivers.video_drivers import VideoStreamer
from constants import *

class Line:
    def __init__(self, line):
        self.line_origin = None
        self.line_tip = None

        # Comparing line heights to find out which point is the tip 
        # and which point is the origin
        if line[0][1] > line[1][1]:
            self.line_origin = numpy.array([line[0][0], line[0][1]])
            self.line_tip = numpy.array([line[1][0], line[1][1]])
        else:
            self.line_origin = numpy.array([line[1][0], line[1][1]])
            self.line_tip = numpy.array([line[0][0], line[0][1]])

        if self.line_origin[0] > CAMERA_IMAGE_WIDTH:
            self.line_origin[0] =  CAMERA_IMAGE_WIDTH
        elif self.line_origin[0] < 0:
            self.line_origin[0] = 0

        if self.line_origin[1] > CAMERA_IMAGE_HEIGHT:
            self.line_origin[1] = CAMERA_IMAGE_HEIGHT
        elif self.line_origin[1] < 0:
            self.line_origin[1] = 0

        if self.line_tip[0] > CAMERA_IMAGE_WIDTH:
            self.line_tip[0] =  CAMERA_IMAGE_WIDTH
        elif self.line_tip[0] < 0:
            self.line_tip[0] = 0

        if self.line_tip[1] > CAMERA_IMAGE_HEIGHT:
            self.line_tip[1] = CAMERA_IMAGE_HEIGHT
        elif self.line_tip[1] < 0:
            self.line_tip[1] = 0
    
    def __repr__(self):
        return f"[O: ({self.line_origin[0]}, {self.line_origin[1]})," \
               f" T: ({self.line_tip[0]}, {self.line_tip[1]})," \
               f" L: {int(self.get_euclidian_distance())}]"

    def get_euclidian_distance(self):
        return numpy.linalg.norm(self.line_origin - self.line_tip)
    
    def check_min_line_length(self):
        if self.get_euclidian_distance() > IMAGE_LINES_MIN_LENGTH:
            return True
        else:
            return False

    def draw(self, output_image, color):
        cv2.arrowedLine(img = output_image,
                        pt1 = self.line_origin,
                        pt2 = self.line_tip,
                        color = color,
                        thickness =  IMAGE_LINES_THICKNESS)

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
        left_line, middle_line, right_line = self.get_guiding_lines(lines)

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
                                            lines = lines,
                                            left_line = left_line,
                                            middle_line = middle_line,
                                            right_line = right_line)

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
        line_list = []
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
            
            rect_middle_line = None
            rect_middle_line1 = Line([middle1, middle3])
            rect_middle_line2 = Line([middle2, middle4])

            if rect_middle_line1.get_euclidian_distance() > rect_middle_line2.get_euclidian_distance():
                rect_middle_line = rect_middle_line1
            else:
                rect_middle_line = rect_middle_line2

            if rect_middle_line.check_min_line_length():
                line_list.append(rect_middle_line)
           
        return rectangle_outlines, line_list
    
    def get_guiding_lines(self, lines):
        left_lines = []
        right_lines = []

        for line in lines:
            if line.line_origin[0] < CAMERA_IMAGE_WIDTH / 2:
                left_lines.append(line)
            else:
                right_lines.append(line)

        left_lines.sort(key = lambda line : line.get_euclidian_distance(), reverse = True)
        right_lines.sort(key = lambda line : line.get_euclidian_distance(), reverse = True)

        print("Left Lines: ")
        print(left_lines)
        print("Right Lines: ")
        print(right_lines)

        left_line = None
        middle_line = None
        right_line = None

        if len(left_lines) > 0:
            left_line = left_lines[0]
        else:
            left_line = Line([[0, CAMERA_IMAGE_HEIGHT], [0, 0]])

        if len(right_lines) > 0:
            right_line = right_lines[0]
        else:
            right_line = Line([[CAMERA_IMAGE_WIDTH, CAMERA_IMAGE_HEIGHT], [CAMERA_IMAGE_WIDTH, 0]])

        middle_line = Line([((left_line.line_origin + right_line.line_origin) / 2).astype(int), 
                            ((left_line.line_tip + right_line.line_tip) / 2).astype(int)])

        return left_line, middle_line, right_line


    def draw_output(self, output_frame, contours, rectangle_outlines, lines, left_line, middle_line, right_line):
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

        if IMAGE_DISPLAY_ALL_LINES:
            for line in lines:
                line.draw(output_frame, IMAGE_LINES_COLOR)

        if IMAGE_DISPLAY_GUIDING_LINES:
            left_line.draw(output_frame, IMAGE_LINES_LEFT_LINE_COLOR)
            middle_line.draw(output_frame, IMAGE_LINES_MIDDLE_LINE_COLOR)
            right_line.draw(output_frame, IMAGE_LINES_RIGHT_LINE_COLOR)

        return output_frame

    def close(self):
        if self.is_debug:
            self.video_streamer.close()
        
        
