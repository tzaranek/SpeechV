#!/usr/bin/python -u

import log


import threading
import win32file
import win32api


import voice
import time
import sys
from globs import gui


if __name__ == "__main__":
    try:
        t = threading.Thread(target=voice.voiceLoop)
        t.daemon = True
        t.start()

        gui.start()

    except Exception as e:
        log.error("speechV.py:", e)
        sys.exit(1)
