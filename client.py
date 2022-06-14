import socket
import json
from Messenger import Messenger
from commons import SERVER_COMMANDS, CLIENT_MESSAGE_FIELDS, SERVER_MESSAGE_FIELDS

SERVER_IP = "127.0.0.1"
SERVER_PORT = 1999

CLIENT_IP = "127.0.0.1"
CLIENT_PORT = 2000

UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_socket.bind((CLIENT_IP, CLIENT_PORT))
UDP_socket.settimeout(1)
messenger = Messenger()

messenger.openConnection(UDP_socket, SERVER_IP, SERVER_PORT)

def __decodeJson__(jsonStr):
    try:
        return json.loads(jsonStr)
    except ValueError as error:
        print("Unformated message received:", jsonStr)
    except TypeError as error:
        print("Unformated message received:", jsonStr)

while (True):
    userInput = input("Digite um comando para enviar ao servidor. Digite 'exit' para sair do programa.\n")
    data = {}
    data[CLIENT_MESSAGE_FIELDS.CLIENT_ADDRESS.value] = [CLIENT_IP, CLIENT_PORT]

    if (userInput == "exit"):
        break
    if (userInput == "help"):
        data[CLIENT_MESSAGE_FIELDS.COMMAND.value] = SERVER_COMMANDS.HELP.value

        dataJson = json.dumps(data)
        messenger.sendMessage(dataJson, UDP_socket, SERVER_IP, SERVER_PORT)
        serverMessage = messenger.receiveMessage(UDP_socket)
        while not serverMessage:
            serverMessage = messenger.receiveMessage(UDP_socket)
    
        messageJson = __decodeJson__(serverMessage)
        status = messageJson[SERVER_MESSAGE_FIELDS.STATUS.value]
        payload = messageJson[SERVER_MESSAGE_FIELDS.PAYLOAD.value]
        for key in payload:
            print(key, "-", payload[key])
        print("\n")

messenger.closeConnection(UDP_socket, SERVER_IP, SERVER_PORT)

