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

    def search_for_clients(self):
        self.client_socket, self.client_address = self.server_socket.accept()
        print("Connection received from: ", self.client_address)

    def is_client_connected(self):
        if self.client_socket:
            return True
        else:
            return False

    def send_data(self, frame):
        if self.is_client_connected():
            data = pickle.dumps(frame)
            message = struct.pack("Q", len(data)) + data
            self.client_socket.sendall(message)
    
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

    def display_data(self):
        data = b""
        payload_size = struct.calcsize("Q")

        while True:
            while len(data) < payload_size:
                packet = self.client_socket.recv(4 * 1024)
                if not packet:
                    break
                data += packet
            
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]

            while len(data) < msg_size:
                data += self.client_socket.recv(4 * 1024)

            frame_data = data[:msg_size]
            data = data[msg_size:]
            frame = pickle.loads(frame_data)

            cv2.imshow("Debug", frame)

    def close(self):
        self.client_socket.close()