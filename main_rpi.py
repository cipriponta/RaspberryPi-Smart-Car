import argparse
import time
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
            processed_frame = image_processor.get_processed_frame()
            time.sleep(LOOP_DELAY)
  
    finally:
        image_processor.close()   

if __name__ == "__main__":
    main()