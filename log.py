from enum import Enum
import os

SPEECHV_LOG_PATH = os.path.join(
        os.path.realpath(os.path.dirname(__file__)), 'log.txt')
LOGFILE = open(SPEECHV_LOG_PATH, 'w')

# Use these functions like you would print
def error(*args, **kwargs):
    print('error: ',file=LOGFILE, end='')
    print(*args, file=LOGFILE, **kwargs)
    LOGFILE.flush()

def warn(*args, **kwargs):
    print('warn: ', file=LOGFILE, end='')
    print(*args, file=LOGFILE, **kwargs)
    LOGFILE.flush()

def info(*args, **kwargs):
    print('info: ', file=LOGFILE, end='')
    print(*args, file=LOGFILE, **kwargs)
    LOGFILE.flush()

def debug(*args, **kwargs):
    print('debug: ', file=LOGFILE, end='')
    print(*args, file=LOGFILE, **kwargs)
    LOGFILE.flush()


class ParseError(Enum):
    ALT = "ALT"
    HOLD = "HOLD"
    RESIZE = "RESIZE"
    BROWSER = "BROWSER"
    HELP = "HELP"


class Logger:
    @staticmethod
    def log(parse_type, command):
        warn("Parsing {} command failed. Could not recognize: {}".format(
            parse_type, command))


