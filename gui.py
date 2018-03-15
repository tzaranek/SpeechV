import log


from tkinter import *
from enum import Enum
import platform
import os
import signal
import sys
from time import sleep
from threading import Thread

# def modeStr(m):
# 	if m == Mode.COMMAND:
# 		return "Command"
# 	elif m == Mode.TEXT:
# 		return "Text"
# 	elif m == Mode.HELP:
# 		return "Text"
# 	else:
# 		raise

def modeStr(m):
	if m & 2**5:
		return "RECORDING"
	elif m & 2**3:
		return "Insert"
	elif m & 2**2:
		return "Follow"
	elif m & 2**1:
		return "Holding"
	elif m == 0:
		return "Normal"
	elif m == "":
		return ""
	else:
		return "Normal"

def statusStr(s):
	if s == Status.READY:
		return "Ready"
	elif s == Status.PROCESSING:
		return "Processing"
	elif s == Status.RECORDING:
		return "Recording"
	elif s == Status.SETTINGS:
		return "Settings"
	elif s == Status.INITIALIZING:
		return "Initializing"
	else:
		raise

#Mode definitions
class Mode(Enum):
	COMMAND = 1
	TEXT = 2
	HELP = 3

class Status(Enum):
	READY = 1
	PROCESSING = 2
	RECORDING = 3
	SETTINGS = 4
	INITIALIZING = 5


#Color codings for different modes
RECORDING = "#EC7063"	#Red
RECOGNIZED = "#3972CE"	#Blue
HELP = "#E5E7E9"		#Off-white
READY = "#52BE80"		#Green

class GUI:
	#These positions were hard-coded for CAEN windows 10
	#TODO:  Find a better way to get the positions
	#       Or hard code for Chun-Han/other OS configurations
	def getPositions(self):
                #Get the resolution from the OS
		s_width = self.root.winfo_screenwidth()
		s_height = self.root.winfo_screenheight()

		#Set locations for different GUI positions
		self.TOP = "+0"
		self.BOTTOM = "+" + str(s_height - 170)
		self.LEFT = "+0"
		self.RIGHT = "+" + str(s_width - 190)
		

	#Returns a string formatted for use with the geometry function
	def strCoordinate(self, x, y):
		return "+" + str(x) + "+" + str(y)

	#Function to update the GUI to show that it is recording
	#We should probably find a better way to do this
	#So that we don't have to manually call this every time
	def startRecording(self):
		self.status = Status.RECORDING
		self.label.config(bg=RECORDING)

	def endRecording(self):
		self.textLock = True
		self.setText("Enter a\nmacro name", True)

	def macroNameEntered(self, name):
		self.setText("Name: " + name + "\nSay yes to confirm\nSay no to retry", True)
		
	def macroNameConfirmed(self):
		self.status = Status.READY
		self.label.config(bg=READY)
		self.textLock = False
		self.updateText()

	#Update the GUI to "Ready"
	def ready(self):
		self.status = Status.READY
		self.updateText()

	def processing(self):
		self.status = Status.PROCESSING
		self.updateText()

	#Updates the last 3 used commands to display
	def updateCommands(self, cmd):
		self.recent[2] = self.recent[1]
		self.recent[1] = self.recent[0]
		self.recent[0] = cmd
		self.updateText()

	#set the GUI to the given mode
	def setMode(self, m):		
		self.mode = m
		self.updateText()
		self.label.bind("<Enter>", self.enter)
		self.getPositions()

	#Update the text in the GUI
	def updateText(self):
		s = ("Status: " + statusStr(self.status) + \
			  "\nMode: " + modeStr(self.mode))
		
		s += "\nRecent Commands: "
		for cmd in self.recent:
			s += "\n"
			s += cmd
		self.setText(s)

	#Restores the last mode before the unrecognized command
	def restoreText(self, text):
		sleep(2)
		self.setText(text)

	#Displays an error and spawns a thread to restore the old mode later
	def showError(self, error):
		text = self.getText()
		self.label.config(font=("Courier", 8))
		self.setText(error)
		t = Thread(target=self.restoreText, args=[text])
		t.start()

	#Display the help menu
	def settingsMode(self, type="DEFAULT"):
		if self.status != Status.READY:
			raise AttributeError("Tried to open settings while busy")
		if hasattr(self, 'window'):
			self.window.destroy()

		self.setText("Settings\nMenu!")
		if type=='DEFAULT':
			file_in = "settings_root.txt"
		elif type=='MACRO':
			file_in = "settings_macro.txt"
		elif type=='ALIAS':
			file_in = "settings_alias.txt"
		with open(file_in, 'r') as text_file:
			help_text = text_file.read()

		self.status = Status.SETTINGS
		self.window = Toplevel()
		canvas = Canvas(master=self.window, height=600, width=1000)
		canvas.grid()
		canvas.create_text((5,5), anchor="nw", text=help_text, width=900)
		self.window.geometry(self.LEFT + self.TOP)
	
	def closeSettings(self):
		if self.status != self.SETTINGS:
			raise AttributeError("Tried to close settings that doesn't exist!")

	#Called upon closing the help menu
	def closeHelpMenu(self):
		self.setMode(0)
		self.window.destroy()

	#Display the help menu
	def helpMode(self, type="DEFAULT"):
		if hasattr(self, 'window'):
		    self.window.destroy()

		self.setText("Help\nMenu!")
		if type=='browser':
			file_in = "browser_help.txt"
		else:
			file_in = "help_text.txt"
		with open(file_in, 'r') as text_file:
			help_text = text_file.read()

		self.status = Status.HELP
		self.window = Toplevel()
		canvas = Canvas(master=self.window, height=600, width=1000)
		canvas.grid()
		canvas.create_text((5,5), anchor="nw", text=help_text, width=900)
		self.window.geometry(self.LEFT + self.TOP)

	#Called upon closing the help menu
	def closeHelpMenu(self):
		self.setMode(0)
		self.window.destroy()

	#Returns the current GUI mode
	def getMode(self):
		return self.mode

	#Moves the window to the given coordinates
	def moveWindow(self, x, y):
		self.root.geometry(self.strCoordinate(x, y))

	#Handles when the mouse enters the window
	#Will move the GUI out of the way
	def enter(self, event):
		if self.right:
			loc = self.LEFT + self.BOTTOM
			self.right = False
		else:
			loc = self.RIGHT + self.BOTTOM
			self.right = True

		#Move window
		self.root.geometry(loc)

	#Sets the text on the GUI
	def setText(self, s, override=False):
		if self.textLock and not override:
			return
		self.text.set(s)

	#Returns the currently displayed text
	def getText(self):
		return self.text.get()

	#Launch the GUI
	def start(self):
		self.root.mainloop()

	#Constructor for the GUI class
	#Initializes the Tkinter GUI object, binds the mouse hover event
	#and sets the object's properties
	def __init__(self):
		#Create the GUI object and set window properties
		self.root = Tk()

		#Create member variables first to populate strings
		self.recent = ["None", "None", "None"]
		self.mode = 0
		self.textLock = False
		self.status = Status.INITIALIZING

		#Setup window properties
		self.root.attributes("-topmost", True)

		#Set up the frame and label properties
		back = Frame(master=self.root,bg='black')
		back.pack_propagate(0) #Don't allow the widgets inside to determine the frame's width / height
		back.pack(fill=BOTH, expand=1) #Expand the frame to fill the root window
		self.root.geometry("100x100")
		self.text = StringVar()
		self.label = Label(back, textvariable=self.text)
		self.label.pack()

		#These are way bigger than needed but it shouldn't matter
		#As long as they're bigger than the frame and the text
		self.label.config(width=30, height=10)
		self.label.config(font=("Courier", 8))
		self.label.config(bg=READY)

		#Calculate screen size and move the window to the bottom right
		self.getPositions()
		self.root.geometry(self.RIGHT + self.BOTTOM)
		self.right = True

		#Fill in the GUI text
		self.updateText()


if __name__ == "__main__":
	#Let us create a default GUI for testing
	tmp = GUI()
	tmp.start()
