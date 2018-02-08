from enum import Enum

class ParseError(Enum):
    ALT = "ALT"
    HOLD = "HOLD"
    RESIZE = "RESIZE"


class Logger:
    @staticmethod
    def log(parse_type, command):
        print("Parsing {} command failed. Could not recognize: {}".formt(
            parse_type, command))


