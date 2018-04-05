import log


from tkinter import *
from enum import Enum
import platform
import os
import signal
import sys
import math
from time import sleep
from threading import Thread
from mode import *
from word2number import w2n

import settings

def statusStr(s):
	return s.name.title()

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
	HELP = 6


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
		log.debug(str(s_width) + " " + str(s_height))
		log.debug(str(self.root.winfo_height()) + ', ' + str(self.root.winfo_width()))

		#Set locations for different GUI positions
		self.TOP = "+0"
		self.BOTTOM = "+" + str(s_height - (90 + self.root.winfo_height()))
		self.LEFT = "+0"
		self.RIGHT = "+" + str(s_width - (self.root.winfo_width()))
	
	def resizeWindowHelper(self, size):
		self.root.geometry(str(size)+'x'+str(size))
		self.root.update()
		self.modeLabel.config(width=15, font=("Courier bold", int(max(148, size)/20)), borderwidth=5, relief="raised")
		self.recentLabel1.config(width=15, font=("Courier", int(max(148, size)/20)), borderwidth=5, relief="sunken")
		self.recentLabel2.config(width=15, font=("Courier", int(max(148, size)/20)), borderwidth=5, relief="ridge")
		self.recentLabel3.config(width=15, font=("Courier", int(max(148, size)/20)), borderwidth=5, relief="solid")
		self.statusLabel.config(width=15, font=("Courier", int(max(148, size)/20)), borderwidth=5, relief="groove")
		self.modeLabel.grid(row=0,column=1,pady=10, padx=10)
		self.recentLabel1.grid(row=1,column=1,padx=0)
		self.recentLabel2.grid(row=2,column=1)
		self.recentLabel3.grid(row=3,column=1)
		self.statusLabel.grid(row=5, column=1, pady=10)
		self.back.grid(row=1, column=1)
		self.root.grid_columnconfigure(0, weight=1)
		self.root.grid_columnconfigure(2, weight=1)
		#148 is the minimum width we can have
		self.getPositions()
		if self.right:
			self.root.geometry(self.RIGHT + self.BOTTOM)
		else:
			self.root.geometry(self.RIGHT + self.BOTTOM)


	def resizeWindow(self, tokens):
		if len(tokens) == 0:
			return
		if isinstance(tokens[0], int):
			size = tokens[0]
		else:
			if isinstance(tokens, list):
				tokens = ' '.join(tokens)
			size = w2n.word_to_num(tokens.lower())

		self.resizeWindowHelper(size)
		
		config = settings.loadConfig()
		config["SETTINGS"]["WINDOW_SIZE"] = size
		settings.saveConfig(config)


	#Returns a string formatted for use with the geometry function
	def strCoordinate(self, x, y):
		return "+" + str(x) + "+" + str(y)

	#Function to update the GUI to show that it is recording
	#We should probably find a better way to do this
	#So that we don't have to manually call this every time
	def startRecording(self):
		self.status = Status.RECORDING
		self.recording = True


	def endRecording(self):
		self.namingMacro = True
		self.modeText.set("Enter a macro name")

	def macroNameEntered(self, name):
		self.modeText.set("Name: " + name + "\nSay yes to confirm\nSay no to retry")
		
	def macroNameConfirmed(self):
		self.status = Status.READY
		self.namingMacro = False
		self.recording = False
		self.modeText.set("Navigation")

	#Update the GUI to "Ready"
	def ready(self):
		if self.recording == False:
			self.statusText.set("Ready")
		else:
			self.statusText.set("Recording")

	def processing(self):
		self.statusText.set("Processing...")

	#Updates the last 3 used commands to display
	def updateCommands(self, cmd):
		self.recent[2].set(self.recent[1].get())
		self.recent[1].set(self.recent[0].get())
		if len(cmd) > 15:
			cmd = cmd[:15] + '...'
		self.recent[0].set(cmd)

		#self.updateText()

	#set the GUI to the given mode
	def setMode(self, m):		
		self.mode = m
		if self.namingMacro:
			return
		self.modeText.set(m.name.lower().capitalize())


	#Displays an error for a few seconds, then returns control to the user
	def showError(self, error):
		self.statusText.set(error)
		sleep(3)
		# t = Thread(target=self.restoreText, args=[text])
		# t.start()

	#Display the help menu
	def settingsMode(self, macros, type="DEFAULT"):
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
		
		help_text += "\n\n\tcurrent macros:"
		for macro in macros:
			m = "\n\t" + macro + ": " + ', '.join(macros[macro])
			help_text += m
		self.status = Status.SETTINGS
		self.window = Toplevel()
		self.window.attributes("-topmost", True)
		canvas = Canvas(master=self.window, height=600, width=1000)
		canvas.grid()
		canvas.create_text((5,5), anchor="nw", text=help_text, width=900)
		self.window.geometry(self.LEFT + self.TOP)
	
	def closeSettings(self):
		self.window.destroy()
		pass

	#Called upon closing the help menu
	def closeHelpMenu(self):
		self.window.destroy()
		pass

	#Display the help menu
	def helpMode(self, type='default'):
		if hasattr(self, 'window'):
		    self.window.destroy()

		self.setText("Help\nMenu!")
		file_in = "help_menus/"+ type + ".txt"
		
		with open(file_in, 'r') as text_file:
			help_text = text_file.read()

		self.status = Status.HELP
		log.info("Help file opened: ", file_in)
		self.window = Toplevel()
		self.window.attributes("-topmost", True)
		canvas = Canvas(master=self.window, height=900, width=800, background="#303030")
		canvas.grid()
		canvas.create_text((5,5), anchor="nw", text=help_text, width=700, font=("Arial", 14), fill="#FFFFFF")
		self.window.geometry(self.LEFT + self.TOP)

	#Returns the current GUI mode
	def getMode(self):
		return self.mode

	#Moves the window to the given coordinates
	def moveWindow(self, x, y):
		self.root.geometry(self.strCoordinate(x, y))

	#Handles when the mouse enters the window
	#Will move the GUI out of the way
	def enter(self, event=None):
		log.info("Mouse entered the GUI!")
		if self.right:
			loc = self.LEFT + self.BOTTOM
			self.right = False
		else:
			loc = self.RIGHT + self.BOTTOM
			self.right = True

		#Move window
		self.root.geometry(loc)

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
		self.root.title("SpeechV")

		#Create member variables first to populate strings
		self.recent = ["None", "None", "None"]
		self.mode = GlobalMode.NAVIGATE
		self.status = Status.INITIALIZING
		self.recording = False
		self.namingMacro = False

		#Setup window properties
		self.root.attributes("-topmost", True)
		self.root.configure(background='#4C4C4C')

		#Set up the frame and label properties
		self.back = Frame(master=self.root,bg='#4C4C4C')
		self.back.pack_propagate(0) #Don't allow the widgets inside to determine the frame's width / height
		self.back.pack(fill=BOTH, expand=0) #Expand the frame to fill the root window

		config = settings.loadConfig()
		s = config["SETTINGS"]["WINDOW_SIZE"]
		self.root.geometry(str(s) + "x" + str(s))
		self.root.update()
		self.modeText = StringVar()
		self.recent = [StringVar(), StringVar(), StringVar()]
		self.statusText = StringVar()
		self.modeText.set("Configuration")
		self.recent[0].set("test2")
		self.recent[1].set("test3")
		self.recent[2].set("test4")
		self.statusText.set("test5")
		
		self.modeLabel = Label(self.back, textvariable=self.modeText)
		self.recentLabel1 = Label(self.back, textvariable=self.recent[0], anchor='w')
		self.recentLabel2 = Label(self.back, textvariable=self.recent[1], anchor='w')
		self.recentLabel3 = Label(self.back, textvariable=self.recent[2], anchor='w')
		self.statusLabel = Label(self.back, textvariable=self.statusText)

		#Calculate screen size and move the window to the bottom right
		self.getPositions()
		self.root.geometry(self.RIGHT + self.BOTTOM)
		self.right = True

		self.resizeWindowHelper(s)


if __name__ == "__main__":
	#Let us create a default GUI for testing
	tmp = GUI()
	tmp.start()
