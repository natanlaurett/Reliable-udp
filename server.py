import socket
from Messenger import Messenger

SERVER_IP = "127.0.0.1"
SERVER_PORT = 1999

UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_socket.bind((SERVER_IP, SERVER_PORT))

messenger = Messenger()

while True:
    print("(SERVER)Received Data:", messenger.receiveMessage(UDP_socket))
