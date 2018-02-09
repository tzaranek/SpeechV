from enum import Enum
import platform
import os
import signal
import sys
from time import sleep
from threading import Thread
try:
	from tkinter import *
except:
	from Tkinter import *

#Mode definitions
class Mode(Enum):
	COMMAND = 1
	TEXT = 2
	HELP = 3

#Color codings for different modes
RECORDING = "#EC7063"	#Red
RECOGNIZED = "#52BE80"		#Green
HELP = "#E5E7E9"		#Off-white
READY = "#3972CE"          #Blue

class GUIClass:
	#These positions were hard-coded for CAEN windows 10
	#TODO:  Find a better way to get the positions
	#       Or hard code for Chun-Han/other OS configurations
	def getPositions(self):
                #Get the resolution from the OS
		s_width = self.root.winfo_screenwidth()
		s_height = self.root.winfo_screenheight()

		#Set locations for different GUI positions
		self.TOP = "+0"
		self.BOTTOM = "+" + str(s_height - 125)
		self.LEFT = "+0"
		self.RIGHT = "+" + str(s_width - 200)
		

	#Returns a string formatted for use with the geometry function
	def strCoordinate(self, x, y):
		return "+" + str(x) + "+" + str(y)

	#Function to update the GUI to show that it is recording
	#We should probably find a better way to do this
	#So that we don't have to manually call this every time
	def recording(self):
		self.label.config(bg=RECORDING)

	#Update the GUI to "Ready"
	def ready(self):
		self.label.config(bg=READY)

	#Call when there is a recognized command
	def commandRecognized(self):
			mode = self.getMode()
			self.setText("Success")
			self.label.config(bg=READY)
			t = Thread(target=self.restoreMode, args=[mode])
			t.start()

	#set the GUI to the given mode
	def setMode(self, m):
		if m == Mode.TEXT:
			self.textMode()
		elif m == Mode.COMMAND:
			self.commandMode()
		elif m == Mode.HELP:
			self.helpMode()
		
		self.mode = m
		self.label.bind("<Enter>", self.enter)
		self.getPositions()

	#Updates the GUI to reflect text mode
	def textMode(self):
		self.setText("Text\nMode")
		#self.updateMode(Mode.TEXT)

	#Restores the last mode before the unrecognized command
	def restoreMode(self, m):
		sleep(2)
		self.label.config(font=("Courier", 36))
		self.setMode(m)

	#Displays an error and spawns a thread to restore the old mode later
	def showError(self):
		mode = self.getMode()
		self.label.config(font=("Courier", 20))
		self.setText("Unrecognized\nCommand")
		t = Thread(target=self.restoreMode, args=[mode])
		t.start()

	#Display the help menu
	def helpMode(self):
		self.setText("Help\nMenu!")
		#Implement Help menu
		pass

	#Called upon closing the help menu?
	def closeHelpMenu(self):
		self.setMode(Mode.COMMAND)
		#Close menu
		pass

	#Updates the GUI to reflect command mode
	def commandMode(self):
		self.setText("Command\nMode")
		#self.updateMode(Mode.COMMAND)

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
	def setText(self, s):
		self.text.set(s)

	#Returns the currently displayed text
	def getText(self):
		return self.text.get()

	#Launch the GUI
	def start(self):
		self.root.mainloop()

	#Loop to ensure the GUI is always on top of other windows
	def bringToFront(self):
		while(True):
			self.root.lift()
			sleep(1)

	#Constructor for the GUI class
	#Initializes the Tkinter GUI object, binds the mouse hover event
	#and sets the object's properties
	def __init__(self):
		#Create the GUI object
		self.root = Tk()

		back = Frame(master=self.root,bg='black')
		back.pack_propagate(0) #Don't allow the widgets inside to determine the frame's width / height
		back.pack(fill=BOTH, expand=1) #Expand the frame to fill the root window
		self.root.geometry("200x100")
		self.text = StringVar()
		self.label = Label(back, textvariable=self.text)
		self.label.pack()
		#These are way bigger than needed but it shouldn't matter
		#As long as they're bigger than the frame and the text
		self.label.config(width=20, height=10)
		self.label.config(font=("Courier", 36))
		self.setMode(Mode.COMMAND)

		#Calculate screen size and get positions to move the window
		self.getPositions()

		self.root.geometry(self.RIGHT + self.BOTTOM)
		self.right = True

		t = Thread(target=self.bringToFront)
		t.start()


# if __name__ == "__main__":
# 	#Let us create a default GUI for testing
# 	tmp = GUIClass()
# 	tmp.start()
