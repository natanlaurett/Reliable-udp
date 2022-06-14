import os
import pathlib
import socket
import json
from enum import Enum
from Messenger import Messenger
from commons import SERVER_COMMANDS, CLIENT_MESSAGE_FIELDS, SERVER_MESSAGE_FIELDS

class __CONNECTION_STATUS__(Enum):
    NOT_REGISTERED    = "NOT_REGISTERED"
    REGISTERED        = "REGISTERED"

SERVER_IP = "127.0.0.1"
SERVER_PORT = 1999

messenger = Messenger()
UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_socket.bind((SERVER_IP, SERVER_PORT))

def main():
    openConnections = []

    while True:
        clientMessage = messenger.receiveMessage(UDP_socket)
        if not clientMessage:
            continue

        messageJson = __decodeJson__(clientMessage)
        print("Decoded user message:", messageJson)

        command = messageJson[CLIENT_MESSAGE_FIELDS.COMMAND.value]

        if command == SERVER_COMMANDS.HELP.value:
            availableCommands = {
                "help": "Commands that might help you",
                "ls": "List available files to download",
                "download": "Request the download of a file",
                "upload": "Request to upload a file",
                "register": "Register an account for the user",
                "login": "Login to existing account",
            }

            dataJson = __buildMessageWithPayload__(200, availableCommands)
            __sendToClient__(dataJson, messageJson)
            print("Sent server commands to user.") 

        if command == SERVER_COMMANDS.LS.value:
            currentFiles = os.listdir(str(pathlib.Path().resolve()) + "\\files")
            dataJson = __buildMessageWithPayload__(200, currentFiles)
            __sendToClient__(dataJson, messageJson)

        #if command == SERVER_COMMANDS.DOWNLOAD.value:
            #TODO
        #if command == SERVER_COMMANDS.UPLOAD.value:
            #TODO
        if command == SERVER_COMMANDS.REGISTER.value:
            secrets = {}
            with open('secrets/secrets.json') as json_file:
                secrets = json.load(json_file) 
            
            user = messageJson[CLIENT_MESSAGE_FIELDS.USER.value]
            password = messageJson[CLIENT_MESSAGE_FIELDS.PASSWORD.value]

            secrets[user] = password

            with open('ecrets/secrets.json', 'w') as outfile:
                json.dump(secrets, outfile)

            dataJson = __buildMessageWithPayload__(200, "Registering successfull")
            __sendToClient__(dataJson, messageJson)

        if command == SERVER_COMMANDS.LOGIN.value:
            secrets = {}
            with open('secrets/secrets.json') as json_file:
                secrets = json.load(json_file) 
            
            user = messageJson[CLIENT_MESSAGE_FIELDS.USER.value]
            password = messageJson[CLIENT_MESSAGE_FIELDS.PASSWORD.value]

            if secrets[user] == password:
                openConnections[user] = __CONNECTION_STATUS__.REGISTERED
                dataJson = __buildMessageWithPayload__(200, "Login successfull")
                __sendToClient__(dataJson, messageJson)

            else:
                dataJson = __buildMessageWithPayload__(404, "User not found")
                __sendToClient__(dataJson, messageJson)

def __decodeJson__(jsonStr):
    try:
        return json.loads(jsonStr)
    except ValueError as error:
        print("Unformated message received:", jsonStr)
    except TypeError as error:
        print("Unformated message received:", jsonStr)

def __buildMessageWithPayload__(status, payload):
    data = {}
    data[SERVER_MESSAGE_FIELDS.STATUS.value] = status
    data[SERVER_MESSAGE_FIELDS.PAYLOAD.value] = payload

    return json.dumps(data)

def __sendToClient__(message, messageJson):
    clientAddress = messageJson[CLIENT_MESSAGE_FIELDS.CLIENT_ADDRESS.value]
    clientIp = clientAddress[0]
    clientPort = clientAddress[1]

    messenger.openConnection(UDP_socket, clientIp, clientPort)
    messenger.sendMessage(message, UDP_socket, clientIp, clientPort)
    messenger.closeConnection(UDP_socket, clientIp, clientPort)

main()
