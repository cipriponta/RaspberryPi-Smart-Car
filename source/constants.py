import numpy
import cv2
import enum

## Enums
class IMAGE_OUTPUT(enum.Enum):
    COLOR = 1
    GREYSCALE = 2
    BLURRED = 3
    THRESHOLDED = 4

## Camera Constants
CAMERA_IMAGE_WIDTH = 320
CAMERA_IMAGE_HEIGHT = 240
CAMERA_RESOLUTION = (CAMERA_IMAGE_WIDTH, CAMERA_IMAGE_HEIGHT)
CAMERA_FRAMERATE = 120
CAMERA_SHUTTER_SPEED = 40000
CAMERA_ISO = 800
CAMERA_INIT_TIME = 0.1
CAMERA_ROTATION = 180

## Image Constants 
# Output Image Constants
IMAGE_FORMAT_BGR = "bgr"
IMAGE_OUTPUT_DIMENSION = (1080, 720)

# Threshold Constants
IMAGE_GREYSCALE_MAX_VALUE = 255
IMAGE_BLUR_BLOCK_SIZE = 23
IMAGE_THRESHOLD_BLOCK_SIZE = 31
IMAGE_THRESHOLD_SUBTRACTED_CONSTANT = 17
IMAGE_THRESHOLD_SIGMA_X = 0
IMAGE_THRESHOLD_BLUR_METHOD = cv2.GaussianBlur
IMAGE_THRESHOLD_TYPE = cv2.THRESH_BINARY_INV
IMAGE_THRESHOLD_ADAPTIVE_METHOD = cv2.ADAPTIVE_THRESH_GAUSSIAN_C
IMAGE_CONTOUR_RETRIEVAL_MODE = cv2.RETR_LIST
IMAGE_CONTOUR_APPROX_METHOD = cv2.CHAIN_APPROX_NONE

# Line Filtering Constants
IMAGE_LINES_MIN_LENGTH = 25
IMAGE_LINES_MIN_ANGLE = 20
IMAGE_SLIDING_WINDOW_SECTIONS = 10
IMAGE_SLIDING_WINDOW_BIASES = [
    0.3,            # Point 1
    0.3,            # Point 2
    0.1,            # Point 3
    0.1,            # Point 4
    0.1,            # Point 5
    0.0,            # Point 6
    0.0,            # Point 7
    0.0,            # Point 8
    0.0,            # Point 9
    0.0,            # Point 10
]

# Drawing Elements for Lines
IMAGE_CONTOUR_COLOR = (0, 150, 0)
IMAGE_RECTANGLE_COLOR = (150, 0, 0)
IMAGE_LINES_COLOR = (0, 66, 255)
IMAGE_SLIDING_WINDOW_COLOR = (187, 255, 255)
IMAGE_SLIDING_WINDOW_CENTRE_COLOR = (100, 100, 0)
IMAGE_SLIDING_WINDOW_LEFT_LINE_COLOR = (50, 0, 255)
IMAGE_SLIDING_WINDOW_MIDDLE_LINE_COLOR = (255, 0, 200)
IMAGE_SLIDING_WINDOW_RIGHT_LINE_COLOR = (255, 124, 0)
IMAGE_LINES_THICKNESS = 1
IMAGE_POINT_CIRCLE_RADIUS = 3

# Drawing Elements for Stats
IMAGE_STATS_RECT_COLOR = (255, 255, 255)
IMAGE_STATS_FONT_SIZE = 0.5
IMAGE_STATS_TEXT_COLOR = (0, 0, 255)
IMAGE_STATS_TEXT_THICKNESS = 1
IMAGE_STATS_RECT_COORDS_STARTING_POINT = (CAMERA_IMAGE_WIDTH - 60, 80)
IMAGE_STATS_RECT_COORDS_ENDING_POINT = (CAMERA_IMAGE_WIDTH, 0)
IMAGE_STATS_LINE_ERROR_COORDS_STARTING_POINT = (CAMERA_IMAGE_WIDTH - 60, 20)
IMAGE_STATS_PID_OUTPUT_COORDS_STARTING_POINT = (CAMERA_IMAGE_WIDTH - 60, 40)
IMAGE_STATS_LEFT_MOTOR_DC_COORDS_STARTING_POINT = (CAMERA_IMAGE_WIDTH - 60, 60)
IMAGE_STATS_RIGHT_MOTOR_DC_COORDS_STARTING_POINT = (CAMERA_IMAGE_WIDTH - 60, 80)

# Display Booleans 
IMAGE_OUTPUT_FRAME = IMAGE_OUTPUT.THRESHOLDED
IMAGE_DISPLAY_CONTOURS = False
IMAGE_DISPLAY_BOUNDED_LINES = False
IMAGE_DISPLAY_DIR_LINES = False
IMAGE_DISPLAY_PER_LINES = False
IMAGE_DISPLAY_SLIDING_WINDOW = True
IMAGE_DISPLAY_SLIDING_WINDOW_CENTRE = True
IMAGE_DISPLAY_SLIDING_WINDOW_GUIDING_LINES = True
IMAGE_DISPLAY_SLIDING_WINDOW_GUIDING_LINES_POINTS = True
IMAGE_DISPLAY_STATS= True

## Motor Constants
# Used Pins
PIN_MOTOR_A_EN = 33             # Yellow Cable
PIN_MOTOR_A_IN1 = 31            # Brown Cable
PIN_MOTOR_A_IN2 = 29            # Orange Cable
PIN_MOTOR_B_EN = 32             # White Cable
PIN_MOTOR_B_IN1 = 40            # Purple Cable
PIN_MOTOR_B_IN2 = 38            # Green Cable

# PWM Constants
MOTOR_PWM_FREQ = 500
MOTOR_PWM_NORMAL_DUTY_CYCLE = 60

# PID Constants
MOTOR_PID_LINE_SETPOINT = 0
MOTOR_PID_SAMPLE_TIME = 0.2
MOTOR_PID_KP = 1.0
MOTOR_PID_KI = 0.0005
MOTOR_PID_KD = 0

## Socket Constants
RPI_IP_ADDRESS = "192.168.0.194"
RPI_PORT = 9999
MAX_CONNECIONS = 1
SEGMENT_FORMAT = "L"
RECEIVED_SEGMENT_SIZE = 4 * 1024
CLOSE_SERVER_KEY = 'q'