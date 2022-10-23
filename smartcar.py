import sys
import RPi.GPIO as GPIO
import time

MOTOR_A_EN = 33
MOTOR_A_IN1 = 31
MOTOR_A_IN2 = 29

MOTOR_B_EN = 32
MOTOR_B_IN1 = 40
MOTOR_B_IN2 = 38

def init_GPIO():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(MOTOR_A_EN, GPIO.OUT)
    GPIO.setup(MOTOR_A_IN1, GPIO.OUT)
    GPIO.setup(MOTOR_A_IN2, GPIO.OUT)
    GPIO.setup(MOTOR_B_EN, GPIO.OUT)
    GPIO.setup(MOTOR_B_IN1, GPIO.OUT)
    GPIO.setup(MOTOR_B_IN2, GPIO.OUT)

def run():
    init_GPIO()

    GPIO.output(MOTOR_A_EN, GPIO.HIGH)
    GPIO.output(MOTOR_A_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_A_IN2, GPIO.LOW)

    GPIO.output(MOTOR_B_EN, GPIO.HIGH)
    GPIO.output(MOTOR_B_IN1, GPIO.HIGH)
    GPIO.output(MOTOR_B_IN2, GPIO.LOW)

def stop():
    init_GPIO()
    GPIO.cleanup()

commands = {
    "run" : run,
    "stop" : stop,
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