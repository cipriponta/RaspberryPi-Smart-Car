from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import math
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

    def draw(self, output_frame, color):
        cv2.circle(img = output_frame,
                   center = self.coords,
                   radius = IMAGE_POINT_CIRCLE_RADIUS,
                   color = color,
                   thickness = IMAGE_LINES_THICKNESS)

    def draw_polynomial(points_list, output_frame, color):
        x_coords_list = []
        y_coords_list = []

        for point in points_list:
            x_coords_list.append(point.width)
            y_coords_list.append(point.height)
            if IMAGE_DISPLAY_SLIDING_WINDOW_GUIDING_LINES_POINTS:
                point.draw(output_frame, color)
        
        if IMAGE_DISPLAY_SLIDING_WINDOW_GUIDING_LINES:
            x_coords_array = numpy.array(x_coords_list)
            y_coords_array = numpy.array(y_coords_list)
            coords_array = numpy.stack((x_coords_array, y_coords_array), axis = 1)
            coords_array = coords_array.astype(int)

            cv2.polylines(img = output_frame,
                        pts = [coords_array],
                        isClosed = False,
                        color = color,
                        thickness = IMAGE_LINES_THICKNESS)
        
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
        
    def check_angle(self):
        try:
            angle_rad = math.atan(abs(self.origin.height - self.tip.height) / abs(self.origin.width - self.tip.width))
            angle_deg = math.degrees(angle_rad)
            if angle_deg > IMAGE_LINES_MIN_ANGLE:
                return True
            else:
                return False
        except ZeroDivisionError:
            return False

    def draw(self, output_image):
        cv2.arrowedLine(img = output_image,
                        pt1 = self.origin.coords,
                        pt2 = self.tip.coords,
                        color = IMAGE_LINES_COLOR,
                        thickness =  IMAGE_LINES_THICKNESS)

class SlidingWindow:
    def __init__(self, rect_outline):
        self.rect_outline = rect_outline
        self.polygon_points = numpy.array([
            self.rect_outline[0].coords,
            self.rect_outline[1].coords,
            self.rect_outline[2].coords,
            self.rect_outline[3].coords,
        ])
        self.polygon_points = self.polygon_points.reshape((-1, 1, 2))

        self.mask = None
        self.centre = None

    def get_sliding_window_centre(self, thresholded_frame):
        self.mask = IMAGE_GREYSCALE_MAX_VALUE * numpy.zeros((CAMERA_IMAGE_HEIGHT, CAMERA_IMAGE_WIDTH), dtype = numpy.uint8)
        cv2.fillPoly(img = self.mask,
                     pts = [self.polygon_points],
                     color = [IMAGE_GREYSCALE_MAX_VALUE])
        self.mask = cv2.bitwise_and(thresholded_frame, self.mask)

        contours, _ = cv2.findContours(image = self.mask,
                                       mode = IMAGE_CONTOUR_RETRIEVAL_MODE,
                                       method = IMAGE_CONTOUR_APPROX_METHOD)
        
        if len(contours) != 1:
            self.centre = Point(
                int((self.rect_outline[0].width + self.rect_outline[2].width) / 2),
                int((self.rect_outline[0].height + self.rect_outline[2].height) / 2),
            )
        else:
            moments = cv2.moments(contours[0])
            if moments['m00'] == 0:
                self.centre = Point(
                    int((self.rect_outline[0].width + self.rect_outline[2].width) / 2),
                    int((self.rect_outline[0].height + self.rect_outline[2].height) / 2),
                )
            else:
                self.centre = Point(
                    int(moments['m10'] / moments['m00']),
                    int(moments['m01'] / moments['m00'])
                )

    def draw(self, output_frame):
        if IMAGE_DISPLAY_SLIDING_WINDOW:
            cv2.polylines(img = output_frame,
                          pts = [self.polygon_points],
                          isClosed = True,
                          color = IMAGE_SLIDING_WINDOW_COLOR,
                          thickness = IMAGE_LINES_THICKNESS)
        
        if IMAGE_DISPLAY_SLIDING_WINDOW_CENTRE:
            self.centre.draw(output_frame, IMAGE_SLIDING_WINDOW_CENTRE_COLOR)

class ProcessedContour:
    def __init__(self, contour):
        self.contour = contour
        self.rectangle = cv2.minAreaRect(self.contour)
        self.rectangle_outline = numpy.int0(cv2.boxPoints(self.rectangle))
        self.rect_dir_line = None
        self.rect_per_line = None
        self.sliding_windows = []

        middle1 = Point(int((self.rectangle_outline[0][0] + self.rectangle_outline[1][0]) / 2), 
                        int((self.rectangle_outline[0][1] + self.rectangle_outline[1][1]) / 2))
        middle2 = Point(int((self.rectangle_outline[1][0] + self.rectangle_outline[2][0]) / 2), 
                        int((self.rectangle_outline[1][1] + self.rectangle_outline[2][1]) / 2))
        middle3 = Point(int((self.rectangle_outline[2][0] + self.rectangle_outline[3][0]) / 2), 
                        int((self.rectangle_outline[2][1] + self.rectangle_outline[3][1]) / 2))
        middle4 = Point(int((self.rectangle_outline[3][0] + self.rectangle_outline[0][0]) / 2), 
                        int((self.rectangle_outline[3][1] + self.rectangle_outline[0][1]) / 2))
        
        rect_middle_line1 = Line(middle1, middle3)
        rect_middle_line2 = Line(middle2, middle4)

        if rect_middle_line1.length > rect_middle_line2.length:
            self.rect_dir_line = rect_middle_line1
            self.rect_per_line = rect_middle_line2
        else:
            self.rect_dir_line = rect_middle_line2
            self.rect_per_line = rect_middle_line1

    def get_sliding_windows_points(self, thresholded_frame):
        rect_dir_width_seg = int(math.ceil((self.rect_dir_line.tip.width - self.rect_dir_line.origin.width) 
                                           / IMAGE_SLIDING_WINDOW_SECTIONS))
        rect_dir_height_seg = int(math.ceil((self.rect_dir_line.tip.height - self.rect_dir_line.origin.height) 
                                            / IMAGE_SLIDING_WINDOW_SECTIONS))
        rect_per_width = int(math.ceil(self.rect_per_line.tip.width - self.rect_per_line.origin.width))
        rect_per_height = int(math.ceil(self.rect_per_line.tip.height - self.rect_per_line.origin.height))

        self.sliding_windows.clear()
        for seg_count in range(0, IMAGE_SLIDING_WINDOW_SECTIONS, 1): 
            sliding_window = SlidingWindow([
                Point( 
                    self.rect_dir_line.origin.width + seg_count * rect_dir_width_seg - int(math.ceil(rect_per_width / 2)),
                    self.rect_dir_line.origin.height + seg_count * rect_dir_height_seg - int(math.ceil(rect_per_height / 2))                                                                 
                ),
                Point( 
                    self.rect_dir_line.origin.width + seg_count * rect_dir_width_seg + int(math.ceil(rect_per_width / 2)),
                    self.rect_dir_line.origin.height + seg_count * rect_dir_height_seg + int(math.ceil(rect_per_height / 2))                                                                 
                ),
                Point( 
                    self.rect_dir_line.origin.width + (seg_count + 1) * rect_dir_width_seg + int(math.ceil(rect_per_width / 2)),
                    self.rect_dir_line.origin.height + (seg_count + 1) * rect_dir_height_seg + int(math.ceil(rect_per_height / 2))                                                                 
                ),
                Point( 
                    self.rect_dir_line.origin.width + (seg_count + 1) * rect_dir_width_seg - int(math.ceil(rect_per_width / 2)),
                    self.rect_dir_line.origin.height + (seg_count + 1) * rect_dir_height_seg - int(math.ceil(rect_per_height / 2))                                                                 
                )
            ])

            sliding_window.get_sliding_window_centre(thresholded_frame)       
            self.sliding_windows.append(sliding_window)

    def get_sliding_windows_points_value(self):
        sliding_windows_points = []
        for sliding_window in self.sliding_windows:
            sliding_windows_points.append(sliding_window.centre)
        return sliding_windows_points

    def check_valid(self):
        return self.rect_dir_line.check_min_line_length() and self.rect_dir_line.check_angle()

    def check_if_contour_belongs_to_left_side(self):
        if self.rect_dir_line.origin.width < int(CAMERA_IMAGE_WIDTH / 2):
            return True
        else:
            return False
    
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
            
        if IMAGE_DISPLAY_DIR_LINES:
            self.rect_dir_line.draw(output_frame)
        
        if IMAGE_DISPLAY_PER_LINES:
            self.rect_per_line.draw(output_frame)
        
        if IMAGE_DISPLAY_SLIDING_WINDOW or IMAGE_DISPLAY_SLIDING_WINDOW_CENTRE:
            for sliding_window in self.sliding_windows:
                sliding_window.draw(output_frame)

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
        self.left_side_contours = []
        self.right_side_contours = []

        self.default_left_line_points = []
        self.default_right_line_points = []

        self.left_line_points = []
        self.right_line_points = []
        self.middle_line_points = []

        self.init_sliding_windows_points_for_default_lines()

    def init_sliding_windows_points_for_default_lines(self):
        seg_height = int(math.ceil(CAMERA_IMAGE_HEIGHT / IMAGE_SLIDING_WINDOW_SECTIONS))

        for seg_count in range(0, IMAGE_SLIDING_WINDOW_SECTIONS, 1):
            self.default_left_line_points.append(Point(0, CAMERA_IMAGE_HEIGHT - seg_count * seg_height))
            self.default_right_line_points.append(Point(CAMERA_IMAGE_WIDTH, CAMERA_IMAGE_HEIGHT - seg_count * seg_height))

    def get_line_shift(self):
        self.camera.capture(self.raw_capture, format = IMAGE_FORMAT_BGR)
        self.frame = self.raw_capture.array
        
        # Clear the stream
        self.raw_capture.truncate(0)

        self.get_contours()
        self.get_middle_line()
        error = self.calculate_error()

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

        return error

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
        self.left_side_contours.clear()
        self.right_side_contours.clear()

        for contour in self.contours:
            processed_contour = ProcessedContour(contour)
            if processed_contour.check_valid():
                processed_contour.get_sliding_windows_points(self.thresholded_frame)
                self.processed_contours.append(processed_contour)  

                if processed_contour.check_if_contour_belongs_to_left_side():
                    self.left_side_contours.append(processed_contour)
                else:
                    self.right_side_contours.append(processed_contour)

    def get_middle_line(self):
        self.left_side_contours.sort(key = lambda contour: contour.rect_dir_line.length, reverse=True)
        self.right_side_contours.sort(key = lambda contour: contour.rect_dir_line.length, reverse=True)
        
        self.left_line_points.clear()
        self.right_line_points.clear()
        self.middle_line_points.clear()

        if len(self.left_side_contours) == 0:
            self.left_line_points = self.default_left_line_points.copy()
        else:
            self.left_line_points = self.left_side_contours[0].get_sliding_windows_points_value()

        if len(self.right_side_contours) == 0:
            self.right_line_points = self.default_right_line_points.copy()
        else:
            self.right_line_points = self.right_side_contours[0].get_sliding_windows_points_value()

        for point_count in range(0, IMAGE_SLIDING_WINDOW_SECTIONS, 1):
            self.middle_line_points.append(Point(
                int((self.left_line_points[point_count].width + self.right_line_points[point_count].width) / 2),
                int((self.left_line_points[point_count].height + self.right_line_points[point_count].height) / 2),
            ))

    def calculate_error(self):
        error = 0.0
        for point_count in range(0, IMAGE_SLIDING_WINDOW_SECTIONS, 1):
            error = error + \
                    (self.middle_line_points[point_count].width - (CAMERA_IMAGE_WIDTH / 2)) * \
                    IMAGE_SLIDING_WINDOW_BIASES[point_count]
        return error

    def draw(self, output_frame):
        for contour in self.processed_contours:
            contour.draw(output_frame)

        if IMAGE_DISPLAY_SLIDING_WINDOW_GUIDING_LINES or \
           IMAGE_DISPLAY_SLIDING_WINDOW_GUIDING_LINES_POINTS:
            Point.draw_polynomial(self.left_line_points, output_frame, IMAGE_SLIDING_WINDOW_LEFT_LINE_COLOR)
            Point.draw_polynomial(self.right_line_points, output_frame, IMAGE_SLIDING_WINDOW_RIGHT_LINE_COLOR)
            Point.draw_polynomial(self.middle_line_points, output_frame, IMAGE_SLIDING_WINDOW_MIDDLE_LINE_COLOR)

    def close(self):
        if self.is_debug:
            self.video_streamer.close()
        
        
