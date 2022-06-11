from Encoder import Encoder, DatagramFields, Flags, MAX_DATA_LENGTH, MAX_PACKET_SIZE
from datetime import datetime, timedelta
import random
import socket

enablePacketLoss = False
packetLossRate = 5 # 5%

class Messenger():
    encoder = Encoder()

    activeConnections = {} # {ClientAddress, boolean}
    waitingForAck = {}     # {ClientAddress, [SeqNum1, SeqNum2, ...]}
    lastAck = {}           # {ClientAddress, SeqNum}

    def openConnection(self, udpSocket, ip, port):
        data = {}
        data[DatagramFields.SEQNUM] = 0
        data[DatagramFields.ACKNUM] = 0
        data[DatagramFields.FLAGS] = Flags.START_CONNECTION
        data[DatagramFields.DATA] = ""

        messageInBytes = self.encoder.encodeMessage(data)
        udpSocket.sendto(messageInBytes.encode(), (ip, port))
    
    def closeConnection(self, udpSocket, ip, port):
        data = {}
        data[DatagramFields.SEQNUM] = 0
        data[DatagramFields.ACKNUM] = 0
        data[DatagramFields.FLAGS] = Flags.CLOSE_CONNECTION
        data[DatagramFields.DATA] = ""

        messageInBytes = self.encoder.encodeMessage(data)
        udpSocket.sendto(messageInBytes.encode(), (ip, port))


    def sendMessage(self, message, udpSocket, ip, port):
        splittedMessage = self.__splitMessage__(message)
        self.__sendChunks__(splittedMessage, 0, udpSocket, ip, port)

        while len(self.waitingForAck[(ip, port)]) > 0:
            timeout = datetime.now() + timedelta(seconds = 5)
            while datetime.now() < timeout and len(self.waitingForAck[(ip, port)]) > 0: 
                self.receiveMessage(udpSocket)
                print("Waiting for ack:", self.waitingForAck[(ip, port)])
            
            if len(self.waitingForAck[(ip, port)]) > 0:
                firstLostPacket = min(self.waitingForAck[(ip, port)])
                print("Timeout for ack exceeded. Beggining retransmition from:", firstLostPacket)
                self.__sendChunks__(splittedMessage, firstLostPacket - 1, udpSocket, ip, port)
                

    def __sendChunks__(self, splittedMessage, startPacket, udpSocket, ip, port):
        self.waitingForAck[(ip, port)] = []
        for i in range(startPacket, len(splittedMessage)):
            flagToSend = Flags.WAIT_FOR_NEXT if i < len(splittedMessage) - 1 else Flags.LAST_PACKET
            
            seqNum = i + 1
            self.waitingForAck[(ip, port)].append(seqNum)

            if enablePacketLoss: #simulate packet loss
                randNumber = random.randint(1, 100)
                if randNumber <= packetLossRate and i < len(splittedMessage) - 1: # Second condition must be dropped
                    print("Packet lost!", seqNum)
                    continue

            data = {}
            data[DatagramFields.SEQNUM] = seqNum
            data[DatagramFields.ACKNUM] = 0
            data[DatagramFields.FLAGS] = flagToSend
            data[DatagramFields.DATA] = splittedMessage[i]

            messageInBytes = self.encoder.encodeMessage(data)
            udpSocket.sendto(messageInBytes.encode(), (ip, port))


    def receiveMessage(self, udpSocket):
        try:

            msg, clientAddress = udpSocket.recvfrom(MAX_PACKET_SIZE)
            msgDatagram = self.encoder.decodeMessage(msg.decode())
            
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
                return self.__receiveDataAcking__(msgDatagram, clientAddress, udpSocket)

        except socket.error as udpSocketerror:
            print("Socket timed out")
            return {}
    
    def __splitMessage__(self, message):
        return [message[i : i + MAX_DATA_LENGTH] for i in range(0, len(message), MAX_DATA_LENGTH)]

    def __receiveDataAcking__(self, msgDatagram, clientAddress, udpSocket):
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
            udpSocket.sendto(messageInBytes.encode(), clientAddress)
            
            msg, newMsgAddress = udpSocket.recvfrom(MAX_PACKET_SIZE)
            currDatagram = self.encoder.decodeMessage(msg.decode())
            while (newMsgAddress != clientAddress or 
                   currDatagram[DatagramFields.SEQNUM] != self.lastAck[clientAddress] + 1):
                msg, newMsgAddress = udpSocket.recvfrom(MAX_PACKET_SIZE)
                currDatagram = self.encoder.decodeMessage(msg.decode())


        decodedData += currDatagram[DatagramFields.DATA]

        print("Sending ack of packet", currDatagram[DatagramFields.SEQNUM], "to ", clientAddress)
        ackDatagram[DatagramFields.ACKNUM] = currDatagram[DatagramFields.SEQNUM]
        messageInBytes = self.encoder.encodeMessage(ackDatagram)
        udpSocket.sendto(messageInBytes.encode(), clientAddress)

        return decodedData
