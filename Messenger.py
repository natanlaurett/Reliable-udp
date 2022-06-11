from Encoder import Encoder, DatagramFields, Flags, MAX_DATA_LENGTH

class Messenger():
    encoder = Encoder()

    def sendMessage(self, message, socket, ip, port):
        splittedMessage = self.__splitMessage__(message)

        for i in range(len(splittedMessage)):
            flagToSend = Flags.WAIT_FOR_NEXT if i < len(splittedMessage) - 1 else Flags.LAST_PACKET

            data = {}
            data[DatagramFields.SEQNUM] = i + 1
            data[DatagramFields.ACKNUM] = 0
            data[DatagramFields.FLAGS] = flagToSend
            data[DatagramFields.DATA] = splittedMessage[i]

            messageInBytes = self.encoder.encodeMessage(data)
            socket.sendto(messageInBytes.encode(), (ip, port))

            #TODO retransmit logic

    def receiveMessage(self, socket, ip, port):
        #TODO
        return ""
    
    def __splitMessage__(self, message):
        return [message[i : i + MAX_DATA_LENGTH] for i in range(0, len(message), MAX_DATA_LENGTH)]
