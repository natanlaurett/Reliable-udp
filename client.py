import socket
from Encoder import Encoder, DatagramFields, Flags

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
encoder = Encoder()

data = {}
data[DatagramFields.SEQNUM] = 1
data[DatagramFields.ACKNUM] = 0
data[DatagramFields.FLAGS] = Flags.START_CONNECTION
data[DatagramFields.DATA] = ""
messageInBytes = encoder.encodeMessage(data)

UDP_socket.sendto(messageInBytes.encode(), (SERVER_IP, SERVER_PORT))
