import log


from enum import Enum


class GlobalMode(Enum):
    NAVIGATE = 0
    INSERT   = 1 # forward text directly to topmost application through OS
    FOLLOW   = 2 # expecting text for following a link in the browser
    SETTINGS = 3
    SLEEPING = 4
    HELP = 5


class WordMode(Enum):
    NAVIGATE  = 0
    HIGHLIGHT = 1 # commands select and operate on text

class RecordMode(Enum):
    IDLE       = 0
    RECORDING  = 1
    NAMING     = 2
    CONFIRMING = 3
