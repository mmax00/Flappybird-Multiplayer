import socket

class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def recieve_from_server(self):
        while True:
            data = self.client_socket.recv(1024)
            yield data

    def connect_to_server(self):
        self.client_socket.connect((self.ip, self.port))
        print("Connected to: ", self.ip, ":", str(self.port), sep='')

    def send_msg_to_server(self, msg):
        self.client_socket.sendall(bytes(msg, 'utf-8'))

    def close_connection(self):
        self.client_socket.close()

    def recieve_msg(self):
        data = self.client_socket.recv(1024)
        return data.decode()