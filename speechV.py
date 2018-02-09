import gui
import state
import voice
from threading import Thread

if __name__ == "__main__":
    t = Thread(target=voice.voiceLoop)
    t.daemon = True
    t.start()

    #Create the GUI. MUST be on the main thread
    tmp = gui.GUI()
    tmp.start()
