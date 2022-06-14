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

def main():
    while (True):
        userInput = input("Type a command to send to the server. Type 'exit' to quit.\n")
        data = {}
        data[CLIENT_MESSAGE_FIELDS.CLIENT_ADDRESS.value] = [CLIENT_IP, CLIENT_PORT]

        if (userInput == "exit"):
            break
        if (userInput == "help"):
            data[CLIENT_MESSAGE_FIELDS.COMMAND.value] = SERVER_COMMANDS.HELP.value
            messageJson = __sendToServerAndWaitForResponse__(data)

            status = messageJson[SERVER_MESSAGE_FIELDS.STATUS.value]
            payload = messageJson[SERVER_MESSAGE_FIELDS.PAYLOAD.value]
            for key in payload:
                print(key, "-", payload[key])
            print("\n")

        if (userInput == "ls"):
            data[CLIENT_MESSAGE_FIELDS.COMMAND.value] = SERVER_COMMANDS.LS.value
            messageJson = __sendToServerAndWaitForResponse__(data)
            
            status = messageJson[SERVER_MESSAGE_FIELDS.STATUS.value]
            payload = messageJson[SERVER_MESSAGE_FIELDS.PAYLOAD.value]

            print("Avaliable files:")
            for availableFile in payload:
                print(availableFile)
            print("\n")

        if (userInput == "register"):
            data[CLIENT_MESSAGE_FIELDS.COMMAND.value] = SERVER_COMMANDS.REGISTER.value

            userName = input("Type a user name to use: ")
            userPassword = input("Type a password to your account: ")
            data[CLIENT_MESSAGE_FIELDS.USER.value] = userName
            data[CLIENT_MESSAGE_FIELDS.PASSWORD.value] = userPassword

            messageJson = __sendToServerAndWaitForResponse__(data)
            
            status = messageJson[SERVER_MESSAGE_FIELDS.STATUS.value]
            payload = messageJson[SERVER_MESSAGE_FIELDS.PAYLOAD.value]

            print("Server returned", status)
            print("Message:", payload)
            print("\n")

        if (userInput == "login"):
            data[CLIENT_MESSAGE_FIELDS.COMMAND.value] = SERVER_COMMANDS.LOGIN.value

            userName = input("userName: ")
            userPassword = input("password: ")
            data[CLIENT_MESSAGE_FIELDS.USER.value] = userName
            data[CLIENT_MESSAGE_FIELDS.PASSWORD.value] = userPassword

            messageJson = __sendToServerAndWaitForResponse__(data)
            
            status = messageJson[SERVER_MESSAGE_FIELDS.STATUS.value]
            payload = messageJson[SERVER_MESSAGE_FIELDS.PAYLOAD.value]

            print("Server returned", status)
            print("Message:", payload)
            print("\n")
        
        if (userInput == "download"):
            data[CLIENT_MESSAGE_FIELDS.COMMAND.value] = SERVER_COMMANDS.DOWNLOAD.value
            fileToDownload = input("What file would you like to download? ")
            
            data[CLIENT_MESSAGE_FIELDS.ARGUMENTS.value] = fileToDownload
            messageJson = __sendToServerAndWaitForResponse__(data)
            
            status = messageJson[SERVER_MESSAGE_FIELDS.STATUS.value]
            payload = messageJson[SERVER_MESSAGE_FIELDS.PAYLOAD.value]
            if (status == 200):
                with open('clientFiles/' + fileToDownload, 'w') as text_file:
                    text_file.write(payload)
            else:
                print("Server returned", status)
                print("Message:", payload)
            print("\n")  

def __decodeJson__(jsonStr):
    try:
        return json.loads(jsonStr)
    except ValueError as error:
        print("Unformated message received:", jsonStr)
    except TypeError as error:
        print("Unformated message received:", jsonStr)

def __sendToServerAndWaitForResponse__(data):
    dataJson = json.dumps(data)
    messenger.sendMessage(dataJson, UDP_socket, SERVER_IP, SERVER_PORT)
    serverMessage = messenger.receiveMessage(UDP_socket)
    while not serverMessage:
        serverMessage = messenger.receiveMessage(UDP_socket)

    return __decodeJson__(serverMessage)

main()
messenger.closeConnection(UDP_socket, SERVER_IP, SERVER_PORT)
