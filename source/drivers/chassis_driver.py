import RPi.GPIO 
from constants import *

class ChassisDriver():
    def __init__(self, standing_mode):
        self.standing_mode = standing_mode

        self.left_motor_pwm = None
        self.right_motor_pwm = None

        self.error_sum = 0.0
        self.prev_error = 0.0
        self.output = 0.0
        self.error = 0.0
        self.derivative = 0.0

        self.left_motor_duty_cycle = 0
        self.right_motor_duty_cycle = 0

        self.GPIO_init()

    def __repr__(self):
        return f"Error: {self.error:.2f}\t" \
               f"Error Sum: {self.error_sum:.2f}\t" \
               f"Derivative: {self.derivative:.2f}\t\t" \
               f"Output: {self.output:.2f}\t" \
               f"Left DC: {self.left_motor_duty_cycle}\t" \
               f"Right DC: {self.right_motor_duty_cycle}\t"

    def GPIO_init(self):
        RPi.GPIO.setmode(RPi.GPIO.BOARD)
        RPi.GPIO.setwarnings(False)
        
        RPi.GPIO.setup(PIN_MOTOR_A_EN, RPi.GPIO.OUT)
        RPi.GPIO.setup(PIN_MOTOR_A_IN1, RPi.GPIO.OUT)
        RPi.GPIO.setup(PIN_MOTOR_A_IN2, RPi.GPIO.OUT)
        RPi.GPIO.setup(PIN_MOTOR_B_EN, RPi.GPIO.OUT)
        RPi.GPIO.setup(PIN_MOTOR_B_IN1, RPi.GPIO.OUT)
        RPi.GPIO.setup(PIN_MOTOR_B_IN2, RPi.GPIO.OUT)

        RPi.GPIO.output(PIN_MOTOR_A_IN1, RPi.GPIO.HIGH)
        RPi.GPIO.output(PIN_MOTOR_A_IN2, RPi.GPIO.LOW)
        RPi.GPIO.output(PIN_MOTOR_B_IN1, RPi.GPIO.HIGH)
        RPi.GPIO.output(PIN_MOTOR_B_IN2, RPi.GPIO.LOW)

        self.left_motor_pwm = RPi.GPIO.PWM(PIN_MOTOR_A_EN, MOTOR_PWM_FREQ)
        self.right_motor_pwm = RPi.GPIO.PWM(PIN_MOTOR_B_EN, MOTOR_PWM_FREQ)

    def change_direction(self, error):
        self.pid_control(error)
        self.calculate_duty_cycles()

        if not self.standing_mode:
            self.left_motor_pwm.start(self.left_motor_duty_cycle)
            self.right_motor_pwm.start(self.right_motor_duty_cycle)

    def pid_control(self, error):
        self.error = error
        self.error_sum += (self.error * MOTOR_PID_SAMPLE_TIME)
        self.derivative = (self.error - self.prev_error) / MOTOR_PID_SAMPLE_TIME
        self.output = MOTOR_PID_KP * self.error + MOTOR_PID_KI * self.error_sum + MOTOR_PID_KD * self.derivative
        self.prev_error = self.error

    def calculate_duty_cycles(self):
        self.left_motor_duty_cycle = int(MOTOR_PWM_NORMAL_DUTY_CYCLE + self.output)
        self.right_motor_duty_cycle = int(MOTOR_PWM_NORMAL_DUTY_CYCLE - self.output)

        if self.left_motor_duty_cycle < 0:
            self.left_motor_duty_cycle = 0
        elif self.left_motor_duty_cycle > MOTOR_PWM_NORMAL_DUTY_CYCLE:
            self.left_motor_duty_cycle = MOTOR_PWM_NORMAL_DUTY_CYCLE
        
        if self.right_motor_duty_cycle < 0:
            self.right_motor_duty_cycle = 0
        elif self.right_motor_duty_cycle > MOTOR_PWM_NORMAL_DUTY_CYCLE:
            self.right_motor_duty_cycle = MOTOR_PWM_NORMAL_DUTY_CYCLE

    def close(self):
        self.left_motor_pwm.stop()
        self.right_motor_pwm.stop()
        RPi.GPIO.cleanup()
