from enum import Enum

SPEECHV_LOG_PATH = os.path.join(
        os.path.realpath(os.path.dirname(__path__)), 'log.txt')
LOGFILE = open(SPEECHV_LOG_PATH, 'w')

# Use these functions like you would print
def error(*args, **kwargs):
    print('error: ', end='')
    print(*args, file=LOGFILE, **kwargs)

def warn(*args, **kwargs):
    print('warn: ', end='')
    print(*args, file=LOGFILE, **kwargs)

def info(*args, **kwargs):
    print('info: ', end='')
    print(*args, file=LOGFILE, **kwargs)

def debug(*args, **kwargs):
    print('debug: ', end='')
    print(*args, file=LOGFILE, **kwargs)


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


