import argparse
from source.video_drivers import VideoStreamer
from source.image_processing_drivers import ImageProcessor

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help = "Allows real time debugging of the camera input on another machine", action="store_true")
    args = parser.parse_args()
    
    image_processor = ImageProcessor()
    video_streamer = None

    if args.debug:
        video_streamer = VideoStreamer(port = 9999)
        video_streamer.connect()
        while True:
            video_streamer.search_for_clients()
            if video_streamer.is_client_connected():
                break

    while True:
        frame = image_processor.return_frame()
        if args.debug:
            video_streamer.send_data(frame)
        pass

    if args.debug:
        video_streamer.close()

if __name__ == "__main__":
    main()