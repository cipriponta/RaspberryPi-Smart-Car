import socket
import pickle
import struct
import cv2

class VideoStreamer:
    def __init__(self, port = 0):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name + ".local")
        self.port = port
        self.socket_address = (self.host_ip, self.port)

        self.client_socket = None
        self.client_address = None

    def connect(self):
        self.server_socket.bind(self.socket_address)
        self.server_socket.listen(5)
        print("Listening at: ", self.socket_address)

    def is_client_connected(self):
        if self.client_socket:
            return True
        else:
            return False

    def search_for_clients(self):
        while True:
            self.client_socket, self.client_address = self.server_socket.accept()
            print("Connection received from: ", self.client_address)
            if self.is_client_connected():
                break

    def send_frame(self, frame):
        # To be modified
        if self.is_client_connected():
            self.client_socket.send(frame)
    
    def close(self):
        if self.is_client_connected():
            self.client_socket.close()

class VideoReceiver:
    def __init__(self, host_ip, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host_ip = host_ip
        self.port = port
        self.client_socket_address = (self.host_ip, self.port)
    
    def connect(self):
        self.client_socket.connect(self.client_socket_address)

    def display_frames(self):
        # To be modified
        while True:
            data = self.client_socket.recv(4 * 1024)
            print(data.decode("utf-8"))

    def close(self):
        self.client_socket.close()