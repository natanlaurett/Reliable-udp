from enum import Enum

class DatagramFields(Enum):
    SEQNUM = "SEQNUM"
    ACKNUM = "ACKNUM"
    FLAGS = "FLAGS"
    DATA = "DATA"

class Flags(Enum):
    START_CONNECTION  = "00"
    CLOSE_CONNECTION  = "01"
    WAIT_FOR_NEXT     = "02"
    LAST_PACKET       = "03"
    ACKNOWLEDGE       = "04"

MAX_DATA_LENGTH = 498
MAX_PACKET_SIZE = 512

# SEQ number  4 bytes 0:4
# ACK number  4 bytes 4:8
# SIZE        2 bytes 8:12
# FLAGs       2 Bytes 12:14
# DATA        0-MAX_DATA_LENGTH Bytes
class Encoder:
    def encodeMessage(self, data):
        seqNumInHex = str("0x{:04x}".format(data[DatagramFields.SEQNUM]))[2:6]
        ackNumInHex = str("0x{:04x}".format(data[DatagramFields.ACKNUM]))[2:6]
        size        = str("0x{:04x}".format(len(data[DatagramFields.DATA])))[2:6]
        flags       = data[DatagramFields.FLAGS]        
        dataToSend  = data[DatagramFields.DATA]

        print("Size", size)

        messageInBytes = seqNumInHex + ackNumInHex + size + flags.value + dataToSend

        return messageInBytes

    def decodeMessage(self, messageInBytes):
        size = int(messageInBytes[8 : 12], 16)
        receivedData = messageInBytes[14 : 14 + size]

        data = {}
        data[DatagramFields.SEQNUM] = int(messageInBytes[0 : 4], 16)
        data[DatagramFields.ACKNUM] = int(messageInBytes[4 : 8], 16)
        data[DatagramFields.FLAGS] = messageInBytes[12 : 14]
        data[DatagramFields.DATA] = receivedData

        return data
    
    