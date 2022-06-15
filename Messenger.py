from Encoder import Encoder, DatagramFields, Flags, MAX_DATA_LENGTH, MAX_PACKET_SIZE
from datetime import datetime, timedelta
import random
import socket
import time

ENABLE_PACKET_LOSS = True
PACKET_LOSS_RATE = 5 # 5%
WINDOW_LEN = 10

class Messenger():
    encoder = Encoder()

    activeConnections = {} # {ClientAddress, boolean}
    waitingForAck = {}     # {ClientAddress, [SeqNum1, SeqNum2, ...]}
    lastAck = {}           # {ClientAddress, SeqNum}
    buffer = {}
    ackTimes = {}

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
        print(str(len(splittedMessage)) + " packets to send")

        windowStart = 0
        while (windowStart < len(splittedMessage)):
            if windowStart == self.lastAck:
                print("Warning: we suspect a bug is causing this behavior.")
                break
            
            self.__sendChunks__(splittedMessage, windowStart, udpSocket, ip, port)

            while len(self.waitingForAck[(ip, port)]) > 0:
                timeout = datetime.now() + timedelta(seconds = 5)
                while datetime.now() < timeout and len(self.waitingForAck[(ip, port)]) > 0: 
                    self.receiveMessage(udpSocket)
                    print("Waiting for ack:", self.waitingForAck[(ip, port)])
                
                if len(self.waitingForAck[(ip, port)]) > 0:
                    firstLostPacket = min(self.waitingForAck[(ip, port)])
                    print("Timeout for ack exceeded. Beggining retransmition from:", firstLostPacket)
                    self.__sendChunks__(splittedMessage, firstLostPacket - 1, udpSocket, ip, port)
        
            windowStart += WINDOW_LEN
    
        #allRTTS = [self.ackTimes[key] for key in self.ackTimes]
        #avgRTT = sum(allRTTS) / len(allRTTS)
        #print("Average RTT:", avgRTT)
        #self.ackTimes = {}

    def __sendChunks__(self, splittedMessage, windowStart, udpSocket, ip, port):
        self.waitingForAck[(ip, port)] = []
        for i in range(windowStart, min(len(splittedMessage), windowStart + WINDOW_LEN)):
            flagToSend = Flags.WAIT_FOR_NEXT if i < len(splittedMessage) - 1 else Flags.LAST_PACKET
            
            seqNum = i + 1
            self.waitingForAck[(ip, port)].append(seqNum)

            if ENABLE_PACKET_LOSS: #simulate packet loss
                randNumber = random.randint(1, 100)
                if randNumber <= PACKET_LOSS_RATE and i < len(splittedMessage) - 1: # Second condition must be dropped
                    print("Packet lost!", seqNum)
                    continue

            data = {}
            data[DatagramFields.SEQNUM] = seqNum
            data[DatagramFields.ACKNUM] = 0
            data[DatagramFields.FLAGS] = flagToSend
            data[DatagramFields.DATA] = splittedMessage[i]

            messageInBytes = self.encoder.encodeMessage(data)
            #self.ackTimes[seqNum] = time.time()
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
                self.buffer[clientAddress] = ""
                return {}

            if msgDatagram[DatagramFields.FLAGS] == Flags.CLOSE_CONNECTION.value:
                print("Closing connection with:", clientAddress)
                self.activeConnections[clientAddress] = False
                #del self.waitingForAck[clientAddress]
                #del self.lastAck[clientAddress]
                self.buffer[clientAddress] = ""
                return {}

            if msgDatagram[DatagramFields.FLAGS] == Flags.ACKNOWLEDGE.value:
                self.waitingForAck[clientAddress] = [i for i in self.waitingForAck[clientAddress] if i > msgDatagram[DatagramFields.ACKNUM]]
                #self.ackTimes[msgDatagram[DatagramFields.ACKNUM]] = time.time() - self.ackTimes[msgDatagram[DatagramFields.ACKNUM]]
                print("Received ack for", msgDatagram[DatagramFields.ACKNUM])
                return {}

            if (self.activeConnections[clientAddress] and
                (msgDatagram[DatagramFields.FLAGS] == Flags.WAIT_FOR_NEXT.value or Flags.LAST_PACKET.value)):
                return self.__receiveDataAcking__(msgDatagram, clientAddress, udpSocket)

        except socket.error as udpSocketerror:
            return {}
    
    def __splitMessage__(self, message):
        return [message[i : min(i + MAX_DATA_LENGTH, len(message))] for i in range(0, len(message), MAX_DATA_LENGTH)]

    def __receiveDataAcking__(self, msgDatagram, clientAddress, udpSocket):
        if msgDatagram[DatagramFields.SEQNUM] != self.lastAck[clientAddress] + 1:
            return {}

        currDatagram = msgDatagram
        decodedData = currDatagram[DatagramFields.DATA]
        self.buffer[clientAddress] = self.buffer[clientAddress] + decodedData

        packetToAck = currDatagram[DatagramFields.SEQNUM]

        ackDatagram = {}
        ackDatagram[DatagramFields.SEQNUM] = 0
        ackDatagram[DatagramFields.ACKNUM] = packetToAck
        ackDatagram[DatagramFields.FLAGS] = Flags.ACKNOWLEDGE
        ackDatagram[DatagramFields.DATA] = ""

        if ENABLE_PACKET_LOSS: #simulate packet loss
            randNumber = random.randint(1, 100)
            if randNumber <= PACKET_LOSS_RATE:
                print("Ack lost!", ackDatagram[DatagramFields.ACKNUM])
                return {}

        self.lastAck[clientAddress] = packetToAck
        messageInBytes = self.encoder.encodeMessage(ackDatagram)
        udpSocket.sendto(messageInBytes.encode(), clientAddress)

        if currDatagram[DatagramFields.FLAGS] == Flags.LAST_PACKET.value:
            bufferData = self.buffer[clientAddress]
            self.buffer[clientAddress] = ""
            self.lastAck[clientAddress] = 0
            return bufferData
        return {}
