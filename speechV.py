import gui
import stateWithGui
import voice
from threading import Thread

if __name__ == "__main__":
    #Create the gui
    g = gui.GUI()

    t = Thread(target=voice.voiceLoop, args=[g])
    t.daemon = True
    t.start()

    #Send the gui into its main loop
    g.start()
