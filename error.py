from enum import Enum

class ParseError(Enum):
    ALT = "ALT"
    HOLD = "HOLD"
    RESIZE = "RESIZE"
    BROWSER = "BROWSER"
    HELP = "HELP"


class Logger:
    @staticmethod
    def log(parse_type, command):
        print("Parsing {} command failed. Could not recognize: {}".format(
            parse_type, command))


