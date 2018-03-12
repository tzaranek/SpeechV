#!/usr/bin/python -u

import threading
import win32file
import win32api

import gui
import state
import voice
import log
import time
import sys


if __name__ == "__main__":
    try:
        #Create the gui
        g = gui.GUI()

        t = threading.Thread(target=voice.voiceLoop, args=[g])
        t.daemon = True
        t.start()

        log.debug("Hello?")
        pipe = win32file.CreateFile(
                r'\\.\pipe\named_pipe',
                win32file.GENERIC_READ, 
                win32file.FILE_SHARE_WRITE | win32file.FILE_SHARE_READ,
                None, win32file.OPEN_EXISTING, 0, None)
        log.debug("did pipe work?")
        log.debug(win32api.GetLastError())
        time.sleep(1)
        while True:
            message = win32file.ReadFile(pipe, 4096)
            log.info(message[1].decode())
            time.sleep(1)


        #Send the gui into its main loop
        g.start()

    except Exception as e:
        log.error("speechV.py:", e)
        sys.exit(1)
