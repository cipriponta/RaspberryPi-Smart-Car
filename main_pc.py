from drivers.video_drivers import VideoReceiver

def main():
    video_receiver = VideoReceiver(host_ip = "192.168.0.194", port = 9999)

    try:
        video_receiver.connect()
        video_receiver.display_frames()
    except KeyboardInterrupt:
        print("Connection closed") 
    finally:
        video_receiver.close()

if __name__ == "__main__":
    main()