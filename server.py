import socket
from Encoder import Encoder, DatagramFields, Flags

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
MAX_PACKET_SIZE = 64

UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_socket.bind((SERVER_IP, SERVER_PORT))

encoder = Encoder()

while True:
    msg, client_addr = UDP_socket.recvfrom(MAX_PACKET_SIZE)
    decodedMessage = msg.decode()
    print(decodedMessage)
    msgData = encoder.decodeMessage(decodedMessage)
    print(msgData)