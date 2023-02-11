import argparse
from drivers.image_processing_drivers import ImageProcessor

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help = "Allows real time debugging of the camera input on another machine", action="store_true")
    args = parser.parse_args()

    if args.debug:
        is_debug = True
    else:
        is_debug = False

    image_processor = ImageProcessor(is_debug)   

    for frame in image_processor.camera.capture_continuous(image_processor.raw_capture, format = "bgr"):
        processed_frame = image_processor.process_frame(frame)

    image_processor.close()        

if __name__ == "__main__":
    main()