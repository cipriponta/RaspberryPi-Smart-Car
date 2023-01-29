from source.video_drivers import VideoReceiver

def main():
    video_receiver = VideoReceiver()
    video_receiver.connect()
    video_receiver.display_data()
    video_receiver.close()

if __name__ == "__main__":
    main()