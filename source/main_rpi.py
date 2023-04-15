import argparse
import time
from picamera import exc as PiCameraException
from drivers.image_processing_drivers import ImageProcessor
from drivers.chassis_driver import ChassisDriver
from constants import *

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", 
                        help = "Allows real time debugging of the camera input on another machine", 
                        action="store_true")
    parser.add_argument("--stand", 
                        help = "Used for debugging, the input from the chassis driver is not sent to the wheels", 
                        action="store_true")
    args = parser.parse_args()

    if args.debug:
        is_debug = True
    else:
        is_debug = False

    if args.stand:
        standing_mode = True
    else:
        standing_mode = False

    image_processor = ImageProcessor(is_debug)  
    chassis_controller = ChassisDriver(standing_mode) 

    try:
        while True:
            start_time = time.time()

            line_shift = image_processor.get_line_shift()
            chassis_controller.change_direction(line_shift)

            end_time = time.time()
            duration = round(end_time - start_time, 2)
            if is_debug:
                print("Process duration: {:.2f}".format(duration), end='\t')
                print("Pid stats: ", chassis_controller.get_stats())

    except (BrokenPipeError, ConnectionResetError):
        print("The connection has been closed by the client")
    except (PiCameraException.PiCameraValueError, KeyboardInterrupt):
        print("The connection has been closed by the server")
    finally:
        image_processor.close()   
        chassis_controller.close()

if __name__ == "__main__":
    main()