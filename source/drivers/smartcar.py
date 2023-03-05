import sys
import RPi.GPIO as GPIO
import time
from enum import Enum

class USED_PINS:
    MOTOR_A_EN = 33
    MOTOR_A_IN1 = 31
    MOTOR_A_IN2 = 29

    MOTOR_B_EN = 32
    MOTOR_B_IN1 = 40
    MOTOR_B_IN2 = 38

class CAR_DIRECTION(Enum):
    FRONT = 0
    BACK = 1
    LEFT = 2
    RIGHT = 3

def GPIO_init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(USED_PINS.MOTOR_A_EN, GPIO.OUT)
    GPIO.setup(USED_PINS.MOTOR_A_IN1, GPIO.OUT)
    GPIO.setup(USED_PINS.MOTOR_A_IN2, GPIO.OUT)
    GPIO.setup(USED_PINS.MOTOR_B_EN, GPIO.OUT)
    GPIO.setup(USED_PINS.MOTOR_B_IN1, GPIO.OUT)
    GPIO.setup(USED_PINS.MOTOR_B_IN2, GPIO.OUT)

def motor_controller(direction):
    GPIO_init()

    GPIO.output(USED_PINS.MOTOR_A_EN, GPIO.HIGH)
    GPIO.output(USED_PINS.MOTOR_B_EN, GPIO.HIGH)
    
    if direction == CAR_DIRECTION.FRONT:
        GPIO.output(USED_PINS.MOTOR_A_IN1, GPIO.HIGH)
        GPIO.output(USED_PINS.MOTOR_A_IN2, GPIO.LOW)
        GPIO.output(USED_PINS.MOTOR_B_IN1, GPIO.HIGH)
        GPIO.output(USED_PINS.MOTOR_B_IN2, GPIO.LOW)
    elif direction == CAR_DIRECTION.BACK:
        GPIO.output(USED_PINS.MOTOR_A_IN1, GPIO.LOW)
        GPIO.output(USED_PINS.MOTOR_A_IN2, GPIO.HIGH)
        GPIO.output(USED_PINS.MOTOR_B_IN1, GPIO.LOW)
        GPIO.output(USED_PINS.MOTOR_B_IN2, GPIO.HIGH)
    elif direction == CAR_DIRECTION.LEFT:
        GPIO.output(USED_PINS.MOTOR_A_IN1, GPIO.LOW)
        GPIO.output(USED_PINS.MOTOR_A_IN2, GPIO.LOW)
        GPIO.output(USED_PINS.MOTOR_B_IN1, GPIO.HIGH)
        GPIO.output(USED_PINS.MOTOR_B_IN2, GPIO.LOW)
    elif direction == CAR_DIRECTION.RIGHT:
        GPIO.output(USED_PINS.MOTOR_A_IN1, GPIO.HIGH)
        GPIO.output(USED_PINS.MOTOR_A_IN2, GPIO.LOW)
        GPIO.output(USED_PINS.MOTOR_B_IN1, GPIO.LOW)
        GPIO.output(USED_PINS.MOTOR_B_IN2, GPIO.LOW)

def front():
    motor_controller(CAR_DIRECTION.FRONT)

def back():
    motor_controller(CAR_DIRECTION.BACK)

def right():
    motor_controller(CAR_DIRECTION.RIGHT)

def left():
    motor_controller(CAR_DIRECTION.LEFT)

def stop():
    GPIO_init()
    GPIO.cleanup()

commands = {
    "front" : front,
    "back" : back,
    "left" : left,
    "right" : right,
    "stop": stop,
}

def main():
    args_num = len(sys.argv)
    try:
        if args_num != 2:
            raise Exception("This script accepts only one parameter")
        
        command_executed = False
        for command in commands:
            if command == sys.argv[1]:
                commands[command]()
                command_executed = True
                break

        if command_executed == False:
            exception_string = "Available parameters are:"
            for command in commands: 
                exception_string += "\n"
                exception_string += command      
            raise Exception(exception_string)

    except Exception as exception:
        print(exception)
    

if __name__ == "__main__":
    main()