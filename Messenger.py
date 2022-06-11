from Encoder import Encoder, DatagramFields, Flags, MAX_DATA_LENGTH, MAX_PACKET_SIZE
from datetime import datetime, timedelta

class Messenger():
    encoder = Encoder()

    activeConnections = {} # {ClientAddress, boolean}
    waitingForAck = {}     # {ClientAddress, [SeqNum1, SeqNum2, ...]}
    lastAck = {}           # {ClientAddress, SeqNum}

    def openConnection(self, socket, ip, port):
        data = {}
        data[DatagramFields.SEQNUM] = 0
        data[DatagramFields.ACKNUM] = 0
        data[DatagramFields.FLAGS] = Flags.START_CONNECTION
        data[DatagramFields.DATA] = ""

        messageInBytes = self.encoder.encodeMessage(data)
        socket.sendto(messageInBytes.encode(), (ip, port))
    
    def closeConnection(self, socket, ip, port):
        data = {}
        data[DatagramFields.SEQNUM] = 0
        data[DatagramFields.ACKNUM] = 0
        data[DatagramFields.FLAGS] = Flags.CLOSE_CONNECTION
        data[DatagramFields.DATA] = ""

        messageInBytes = self.encoder.encodeMessage(data)
        socket.sendto(messageInBytes.encode(), (ip, port))


    def sendMessage(self, message, socket, ip, port):
        splittedMessage = self.__splitMessage__(message)
        self.waitingForAck[(ip, port)] = []

        for i in range(len(splittedMessage)):
            flagToSend = Flags.WAIT_FOR_NEXT if i < len(splittedMessage) - 1 else Flags.LAST_PACKET

            seqNum = i + 1
            data = {}
            data[DatagramFields.SEQNUM] = seqNum
            data[DatagramFields.ACKNUM] = 0
            data[DatagramFields.FLAGS] = flagToSend
            data[DatagramFields.DATA] = splittedMessage[i]

            messageInBytes = self.encoder.encodeMessage(data)
            socket.sendto(messageInBytes.encode(), (ip, port))

            self.waitingForAck[(ip, port)].append(seqNum)

        timeout = datetime.now() + timedelta(seconds = 5)
        while (datetime.now() < timeout and len(self.waitingForAck[(ip, port)]) > 0):
            self.receiveMessage(socket)
            print("Waiting for ack:", self.waitingForAck[(ip, port)])


    def receiveMessage(self, socket):
        msg, clientAddress = socket.recvfrom(MAX_PACKET_SIZE)
        msgDatagram = self.encoder.decodeMessage(msg.decode())

        #print(msgDatagram)
        
        if msgDatagram[DatagramFields.FLAGS] == Flags.START_CONNECTION.value:
            print("Oppening connection with:", clientAddress)
            self.activeConnections[clientAddress] = True
            self.waitingForAck[clientAddress] = []
            self.lastAck[clientAddress] = 0
            return {}

        if msgDatagram[DatagramFields.FLAGS] == Flags.CLOSE_CONNECTION.value:
            print("Closing connection with:", clientAddress)
            self.activeConnections[clientAddress] = False
            del self.waitingForAck[clientAddress]
            del self.lastAck[clientAddress]
            return {}

        if msgDatagram[DatagramFields.FLAGS] == Flags.ACKNOWLEDGE.value:
            self.waitingForAck[clientAddress] = [i for i in self.waitingForAck[clientAddress] if i > msgDatagram[DatagramFields.ACKNUM]]
            print("Received ack for", msgDatagram[DatagramFields.ACKNUM])
            return {}

        if (self.activeConnections[clientAddress] and
            (msgDatagram[DatagramFields.FLAGS] == Flags.WAIT_FOR_NEXT.value or Flags.LAST_PACKET.value)):
            return self.__receiveDataAcking__(msgDatagram, clientAddress, socket)
    
    def __splitMessage__(self, message):
        return [message[i : i + MAX_DATA_LENGTH] for i in range(0, len(message), MAX_DATA_LENGTH)]

    def __receiveDataAcking__(self, msgDatagram, clientAddress, socket):
        if msgDatagram[DatagramFields.SEQNUM] != self.lastAck[clientAddress] + 1:
            return {}

        currDatagram = msgDatagram
        decodedData = ""

        ackDatagram = {}
        ackDatagram[DatagramFields.SEQNUM] = 0
        ackDatagram[DatagramFields.FLAGS] = Flags.ACKNOWLEDGE
        ackDatagram[DatagramFields.DATA] = ""

        while (currDatagram[DatagramFields.FLAGS] != Flags.LAST_PACKET.value):
            packetToAck = currDatagram[DatagramFields.SEQNUM]
            self.lastAck[clientAddress] = packetToAck

            decodedData += currDatagram[DatagramFields.DATA]

            print("Sending ack of packet", packetToAck, "to ", clientAddress)
            ackDatagram[DatagramFields.ACKNUM] = packetToAck
            messageInBytes = self.encoder.encodeMessage(ackDatagram)
            socket.sendto(messageInBytes.encode(), clientAddress)

            msg, newMsgAddress = socket.recvfrom(MAX_PACKET_SIZE)
            while newMsgAddress != clientAddress:
                msg, newMsgAddress = socket.recvfrom(MAX_PACKET_SIZE)

            currDatagram = self.encoder.decodeMessage(msg.decode())

        decodedData += currDatagram[DatagramFields.DATA]

        ackDatagram[DatagramFields.ACKNUM] = currDatagram[DatagramFields.SEQNUM]
        messageInBytes = self.encoder.encodeMessage(ackDatagram)
        socket.sendto(messageInBytes.encode(), clientAddress)

        return decodedData
