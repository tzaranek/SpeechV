#!/usr/bin/python -u

import gui
import state
import voice
from threading import Thread
import log

if __name__ == "__main__":
    #Create the gui
    g = gui.GUI()

    t = Thread(target=voice.voiceLoop, args=[g])
    t.daemon = True
    t.start()

    #Send the gui into its main loop
    g.start()
