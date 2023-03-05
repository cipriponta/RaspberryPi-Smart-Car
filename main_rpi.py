import argparse
import time
from picamera import exc as PiCameraException
from drivers.image_processing_drivers import ImageProcessor

LOOP_DELAY = 0.001

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help = "Allows real time debugging of the camera input on another machine", action="store_true")
    args = parser.parse_args()

    if args.debug:
        is_debug = True
    else:
        is_debug = False

    image_processor = ImageProcessor(is_debug)   

    try:
        while True:
            start_time = time.time()
            processed_frame = image_processor.get_processed_frame()
            end_time = time.time()
            print("Process duration: ", end_time - start_time)
            time.sleep(LOOP_DELAY)  

    except (BrokenPipeError, ConnectionResetError):
        print("The connection has been closed by the client")
    except (PiCameraException.PiCameraValueError, KeyboardInterrupt):
        print("The connection has been closed by the server")
    finally:
        image_processor.close()   

if __name__ == "__main__":
    main()