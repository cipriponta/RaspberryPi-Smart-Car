import RPi.GPIO 
from constants import *

class ChassisDriver():
    def __init__(self, standing_mode):
        self.standing_mode = standing_mode
        self.GPIO_init()

    def GPIO_init(self):
        RPi.GPIO.setmode(RPi.GPIO.BOARD)
        RPi.GPIO.setwarnings(False)
        RPi.GPIO.setup(PIN_MOTOR_A_EN, RPi.GPIO.OUT)
        RPi.GPIO.setup(PIN_MOTOR_A_IN1, RPi.GPIO.OUT)
        RPi.GPIO.setup(PIN_MOTOR_A_IN2, RPi.GPIO.OUT)
        RPi.GPIO.setup(PIN_MOTOR_B_EN, RPi.GPIO.OUT)
        RPi.GPIO.setup(PIN_MOTOR_B_IN1, RPi.GPIO.OUT)
        RPi.GPIO.setup(PIN_MOTOR_B_IN2, RPi.GPIO.OUT)

    def change_direction(self):
        # To Be Implemented
        if not self.standing_mode:
            RPi.GPIO.output(PIN_MOTOR_A_EN, RPi.GPIO.HIGH)
            RPi.GPIO.output(PIN_MOTOR_B_EN, RPi.GPIO.HIGH)
            RPi.GPIO.output(PIN_MOTOR_A_IN1, RPi.GPIO.HIGH)
            RPi.GPIO.output(PIN_MOTOR_A_IN2, RPi.GPIO.LOW)
            RPi.GPIO.output(PIN_MOTOR_B_IN1, RPi.GPIO.HIGH)
            RPi.GPIO.output(PIN_MOTOR_B_IN2, RPi.GPIO.LOW)

    def close(self):
        RPi.GPIO.cleanup()
