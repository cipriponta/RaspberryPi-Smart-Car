from drivers.video_drivers import VideoReceiver
from constants import *

def main():
    video_receiver = VideoReceiver(host_ip = RPI_IP_ADDRESS, port = RPI_PORT)

    try:
        video_receiver.connect()
        video_receiver.display_frames()
    except KeyboardInterrupt:
        print("Connection closed") 
    finally:
        video_receiver.close()

if __name__ == "__main__":
    main()