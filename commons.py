from enum import Enum

class SERVER_COMMANDS(Enum):
    HELP              = "help"
    LS                = "ls"
    DOWNLOAD          = "download"
    UPLOAD            = "upload"
    REGISTER          = "register"
    LOGIN             = "login"

class CLIENT_MESSAGE_FIELDS(Enum):
    CLIENT_ADDRESS    = "CLIENT_ADDRESS"
    COMMAND           = "COMMAND"
    ARGUMENTS         = "ARGUMENTS" #Optional
    USER              = "USER"      #Optional
    PASSWORD          = "PASSWORD"  #Optional

class SERVER_MESSAGE_FIELDS(Enum):
    STATUS            = "STATUS"
    PAYLOAD           = "PAYLOAD"