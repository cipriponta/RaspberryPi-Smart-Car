import numpy
import cv2

# Main Loop Constants
LOOP_DELAY = 0.001

# Camera Constants
CAMERA_RESOLUTION = (320, 240)
CAMERA_FRAMERATE = 120
CAMERA_SHUTTER_SPEED = 40000
CAMERA_ISO = 800
CAMERA_INIT_TIME = 0.1
CAMERA_ROTATION = 180

# Image Constants
IMAGE_FORMAT_BGR = "bgr"
IMAGE_OUTPUT_DIMENSION = (1080, 720)

IMAGE_GREYSCALE_MAX_VALUE = 255
IMAGE_THRESHOLD_BLOCK_SIZE = 31
IMAGE_THRESHOLD_SUBTRACTED_CONSTANT = 9
IMAGE_THRESHOLD_BLUR_METHOD = cv2.GaussianBlur
IMAGE_THRESHOLD_TYPE = cv2.THRESH_BINARY_INV
IMAGE_THRESHOLD_ADAPTIVE_METHOD = cv2.ADAPTIVE_THRESH_GAUSSIAN_C

IMAGE_LINES_COLOR = (0, 200, 0)
IMAGE_LINES_THICKNESS = 1

# Debug Server Constants
RPI_IP_ADDRESS = "192.168.0.194"
RPI_PORT = 9999
MAX_CONNECIONS = 1
SEGMENT_FORMAT = "L"
RECEIVED_SEGMENT_SIZE = 4 * 1024
CLOSE_SERVER_KEY = 'q'