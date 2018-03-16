from enum import Enum
import os
import sys

SPEECHV_LOG_PATH = os.path.join(
        os.path.realpath(os.path.dirname(__file__)), 'log.txt')
LOGFILE = open(SPEECHV_LOG_PATH, 'w')

# redirect all stderr to LOGFILE since speechv is invoked such
# that stderr and stdout are not normally observable
#
# NOTE: for this to work, log.py must be imported before all else, in all files
sys.stderr = LOGFILE

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

def blank():
    print('', file=LOGFILE)
    LOGFILE.flush()


def parse_error(parse_type, command):
    warn("Parsing {} command failed. Could not recognize: {}".format(
        parse_type, command))


class ParseError(Enum):
    ALT = "ALT"
    HOLD = "HOLD"
    RESIZE = "RESIZE"
    BROWSER = "BROWSER"
    HELP = "HELP"
    TYPE = "TYPE"
    FOCUS = "FOCUS"

