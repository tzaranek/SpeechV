#!/usr/bin/python -u

import log


import threading
import win32file
import win32api

import gui
import state
import voice
import time
import sys


if __name__ == "__main__":
    try:
        #Create the gui
        g = gui.GUI()

        t = threading.Thread(target=voice.voiceLoop, args=[g])
        t.daemon = True
        t.start()

        #Send the gui into its main loop
        g.start()

    except Exception as e:
        log.error("speechV.py:", e)
        sys.exit(1)
