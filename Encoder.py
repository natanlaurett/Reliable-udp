from enum import Enum

class DatagramFields(Enum):
    SEQNUM = "SEQNUM"
    ACKNUM = "ACKNUM"
    FLAGS = "FLAGS"
    DATA = "DATA"

class Flags(Enum):
    START_CONNECTION = "00"
    CLOSE_CONNECTION = "01"
    WAIT_FOR_NEXT    = "02"
    LAST_PACKAGE     = "03"
    ACKNOWLEDGE      = "04"
    RETRANSMITED     = "05"


# SEQ number  4 bytes 0:4
# ACK number  4 bytes 4:8
# SIZE        2 bytes 8:10
# FLAGs       2 Bytes 10:12
# CHECKSUM    2 Bytes 12:14
# DATA        0-50 Bytes
class Encoder:
    def encodeMessage(self, data):
        seqNumInHex = str("0x{:04x}".format(data[DatagramFields.SEQNUM]))[2:6]
        ackNumInHex = str("0x{:04x}".format(data[DatagramFields.ACKNUM]))[2:6]
        size        = str("0x{:02x}".format(len(data[DatagramFields.DATA])))[2:4]
        flags       = data[DatagramFields.FLAGS]

        messageInBytes = seqNumInHex + ackNumInHex + size + flags.value
        
        checkSum = str(hex(abs(hash(messageInBytes)) % (16 ** 16)))[2:4]
        dataToSend  = data[DatagramFields.DATA]

        messageInBytes += checkSum + dataToSend

        return messageInBytes

    def decodeMessage(self, messageInBytes):
        receivedChecksum = messageInBytes[12 : 14]
        calculatedChecksum = str(hex(abs(hash(messageInBytes[0 : 12])) % (16 ** 16)))[2:4]

        print("Received checksum:", receivedChecksum)
        print("Calculated checksum:", calculatedChecksum)
        #if receivedChecksum != calculatedChecksum:
        #    return {}

        size = int(messageInBytes[8 : 10], 16)
        receivedData = messageInBytes[14 : 14 + size]

        data = {}
        data[DatagramFields.SEQNUM] = int(messageInBytes[0 : 4], 16)
        data[DatagramFields.ACKNUM] = int(messageInBytes[4 : 8], 16)
        data[DatagramFields.FLAGS] = messageInBytes[10 : 12]
        data[DatagramFields.DATA] = receivedData

        return data
    
    