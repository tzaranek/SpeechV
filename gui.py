import log


from tkinter import *
from enum import Enum
import platform
import os
import signal
import sys
import math
from time import sleep
from threading import Thread, Lock
from mode import *
from word2number import w2n

import settings

def statusStr(s):
	return s.name.title()

#Mode definitions
# class Mode(Enum):
# 	COMMAND = 1
# 	TEXT = 2
# 	HELP = 3

class Status(Enum):
	READY = 1
	PROCESSING = 2
	RECORDING = 3
	SETTINGS = 4
	INITIALIZING = 5
	HELP = 6

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
		self.BOTTOM = "+" + str(s_height - (80 + self.root.winfo_height()))
		self.LEFT = "+0"
		self.RIGHT = "+" + str(s_width - (15 + self.root.winfo_width()))


	def resizeWindow(self, tokens):
		if len(tokens) == 0:
			return
		if isinstance(tokens[0], int):
			size = tokens[0]
		else:
			if isinstance(tokens, list):
				tokens = ' '.join(tokens)
			size = w2n.word_to_num(tokens.lower())

		# self.resizeWindowHelper(size)
		self.setupWindow(False, size)

		self.getPositions()
		if self.right:
			self.root.geometry(self.RIGHT + self.BOTTOM)
		else:
			self.root.geometry(self.RIGHT + self.BOTTOM)
		
		self.root.update()
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
		with self.processingLock:
			self.inProcessing = False
		if self.recording == False:
			self.statusText.set("Ready")
		else:
			self.statusText.set("Recording: Ready")

	def processing(self):
		with self.processingLock:
			self.inProcessing = True
		t = Thread(target=self.displayProcessing)
		t.start()

	def displayProcessing(self):
		count = 0
		while self.inProcessing == True:
			with self.processingLock:
				self.statusText.set("Processing"+(count%4)*'.')
				count += 1
			sleep(0.5)

	#Updates the last 3 used commands to display
	def updateCommands(self, cmd):
		if self.recentText[0].get() == "Recent Commands":
			self.recentText[0].set("")
		self.recentText[2].set(self.recentText[1].get())
		self.recentText[1].set(self.recentText[0].get())
		if len(cmd) > 18:
			cmd = cmd[:18] + '...'
		self.recentText[0].set(cmd)

		#self.updateText()

	#set the GUI to the given mode
	def setMode(self, m):		
		self.mode = m
		if self.namingMacro:
			return
		name = m.name.capitalize()
		self.modeText.set(name)
		if name == "Navigate":
			self.modeLabel.config(bg=NAVIGATION)
		elif name == "Insert":
			self.modeLabel.config(bg=INSERTION)
		elif name == "Sleeping":
			self.modeLabel.config(bg=STANDBY)
		elif name == "Help":
			self.modeLabel.config(bg=CONFIGURATION)


	#Displays an error for a few seconds, then returns control to the user
	def showError(self, error):
		#Grab the processingLock to prevent the processing text to overwrite this
		with self.processingLock:
			self.statusText.set(error)
			self.statusLabel.config(fg=STANDBY)
			sleep(3)
			self.statusLabel.config(fg="#000000")
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

	def borderFrame(self, parent, bg='#ff4095', border='#66cdaa', 
		padx_bg=5, pady_bg=5, padx_b=0.2, pady_b=0.2):
		"""When creating a subframe, center it with frame.grid(row=2, column=2)"""

		canvas = Frame(parent, bg=bg)

		# fill border sides
		blank_frame1 = Frame(canvas, bg=border)
		blank_frame2 = Frame(canvas, bg=border)
		blank_frame3 = Frame(canvas, bg=border)
		blank_frame4 = Frame(canvas, bg=border)
		blank_frame1.grid(row=2, column=1, ipadx=padx_b, sticky=N+S)
		blank_frame2.grid(row=2, column=3, ipadx=padx_b, sticky=N+S)
		blank_frame3.grid(row=1, column=2, ipady=pady_b, sticky=W+E)
		blank_frame4.grid(row=3, column=2, ipady=pady_b, sticky=W+E)


		# fill background sides
		blank_frame5 = Frame(canvas, bg=bg)
		blank_frame6 = Frame(canvas, bg=bg)
		blank_frame7 = Frame(canvas, bg=bg)
		blank_frame8 = Frame(canvas, bg=bg)
		blank_frame5.grid(row=2, column=0, padx=padx_bg)
		blank_frame6.grid(row=2, column=4, padx=padx_bg)
		blank_frame7.grid(row=0, column=2, pady=pady_bg)
		blank_frame8.grid(row=4, column=2, pady=pady_bg)

		# fill border corners
		blank_frame9 = Frame(canvas, bg=border)
		blank_frame10 = Frame(canvas, bg=border)
		blank_frame11 = Frame(canvas, bg=border)
		blank_frame12 = Frame(canvas, bg=border)
		blank_frame9.grid(row=1, column=1, ipadx=padx_b/3, ipady=pady_b/3, sticky=S+E)
		blank_frame10.grid(row=1, column=3, ipadx=padx_b/3, ipady=pady_b/3, sticky=S+W)
		blank_frame11.grid(row=3, column=1, ipadx=padx_b/3, ipady=pady_b/3, sticky=N+E)
		blank_frame12.grid(row=3, column=3, ipadx=padx_b/3, ipady=pady_b/3, sticky=N+W)

		return canvas

	def setupWindow(self, init=False, size=0):
		# have self.borderFrame do all the work of maintaining a border and background
		#Setup the grid if this is the first time we are running this function
		#Otherwise, we are using this to resize the window, so just change the label configs
		if init:
			self.modeFrame = self.borderFrame(self.root, bg="#4C4C4C", border='#C9C9C9', padx_bg=4, pady_bg=4)
			self.modeText = StringVar()
			self.modeLabel = Label(self.modeFrame, textvariable=self.modeText)
			self.modeText.set("")
			self.modeLabel.grid(row=2, column=2)
			self.modeFrame.grid(sticky=W+E)

			self.recentFrame = self.borderFrame(self.root, bg="#4C4C4C", border='#C9C9C9', padx_bg=4, pady_bg=4)
			self.recentWrapper = Frame(self.recentFrame)
			self.recentText = [StringVar(), StringVar(), StringVar()]
			self.recentLabels = [None, None, None]

			for i in range(3):
				self.recentLabels[i] = Label(self.recentWrapper, textvariable=self.recentText[i], anchor="w")
				self.recentText[i].set("")
				self.recentLabels[i].grid(row=i)

			self.recentText[0].set("Recent Commands")
			self.recentFrame.grid(row=1, sticky=W+E)
			self.recentWrapper.grid(row=2, column=2)

			self.statusFrame = self.borderFrame(self.root, bg="#4C4C4C", border='#C9C9C9', padx_bg=4, pady_bg=4)

			self.statusText = StringVar()
			self.statusLabel = Label(self.statusFrame, textvariable=self.statusText)
			self.statusText.set(self.status.name.capitalize())
			self.statusLabel.grid(row=2, column=2)
			self.statusFrame.grid(row=2, sticky=W+E)



		self.modeLabel.config(width=18, font=("Courier bold", int(max(148, size)/20)))
		for i in range(3):
			self.recentLabels[i].config(width=18, font=("Courier bold", int(max(148, size)/20)))
		self.statusLabel.config(width=18, font=("Courier bold", int(max(148, size)/20)))



	#Constructor for the GUI class
	#Initializes the Tkinter GUI object, binds the mouse hover event
	#and sets the object's properties
	def __init__(self):
		#Create the GUI object and set window properties
		self.root = Tk()
		self.root.title("SpeechV")

		self.recording = False
		self.namingMacro = False
		self.inProcessing = True
		self.processingLock = Lock()
		self.status = Status.INITIALIZING

		# #Setup window properties
		self.root.attributes("-topmost", True)
		config = settings.loadConfig()
		s = config["SETTINGS"]["WINDOW_SIZE"]
		self.setupWindow(True, s)

		#This has to go after setupWindow so the labels are declared
		self.setMode(GlobalMode.NAVIGATE)
		self.root.update()
		
		# #Calculate screen size and move the window to the bottom right
		self.getPositions()
		self.root.geometry(self.RIGHT + self.BOTTOM)
		self.right = True


if __name__ == "__main__":
	#Let us create a default GUI for testing
	tmp = GUI()
	tmp.start()
