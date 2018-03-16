import log
from gui import GUI

# Globals
#
# While it may be tempting to name this module globals.py, that wouldn't
# play well with the keyword 'globals' when importing

# What we really want is GUI to be a singleton class, but for expediency
# we define one instance as a global variable
gui = GUI()

def start_gui():
    gui.start()
