import socket
from Messenger import Messenger

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000

UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
messenger = Messenger()

message = "Lorem ipsum dolor sit amet, consectetur adipisicing elit," + \
            "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." + \
            " Ut enim ad minim veniam, quis nostrud exercitation ullamco" + \
            " laboris nisi ut aliquip ex ea commodo consequat. Duis aute" + \
            " irure dolor in reprehenderit in voluptate velit esse cillum" + \
            " dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat" + \
            " non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."

messenger.sendMessage(message, UDP_socket, SERVER_IP, SERVER_PORT)
