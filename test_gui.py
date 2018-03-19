import log


from threading import Thread
from gui import *
from time import sleep

#Hacky way to get interactive python shell while GUI is running
#After running any tests you want in this function
#Control-C (or whatever it is on mac) and then hover the gui
#You should get a keyboard interrupt in the interpreter and then
#You can hit enter to start an interactive session
def runTests(gui):
    sleep(1)
    gui.helpMode("firefoxNAVIGATE")
    sleep(3)
    gui.closeHelpMenu()
    sleep(1)
    gui.helpMode("wordNAVIGATE")
    sleep(3)
    gui.helpMode("INSERT")
    sleep(3)
    gui.helpMode("wordFOLLOW")
    sleep(3)
    gui.helpMode("firefoxFOLLOW")
    sleep(3)
    gui.closeHelpMenu()
    
#The GUI library does NOT like it if you run the GUI from anything
#other than the main thread, so hopefully we can 
if __name__ == "__main__":
    gui = GUI()
    thread = Thread(target = runTests, args = [gui])
    thread.start()
    gui.start()
