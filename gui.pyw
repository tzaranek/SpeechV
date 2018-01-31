from Tkinter import *
from enum import Enum
import platform
import os
# from threading import Thread

class Mode(Enum):
	COMMAND = 1
	TEXT = 2

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
		self.RIGHT = "+" + str(s_width - 160)

	#Returns a string formatted for use with the geometry function
	def strCoordinate(self, x, y):
		return "+" + str(x) + "+" + str(y)

	#Function to update the GUI to show that it is recording
	#We should probably find a better way to do this
	#So that we don't have to manually call this every time
	def recording(self):
		#Implement recording notification here
		return

	def updateMode(self, mode):
		if mode == Mode.TEXT:
			self.bg = Label(self.root, image=self.textImage)
		else:
			self.bg = Label(self.root, image=self.commandImage)
		
		self.bg.place(x=0, y=0, relwidth=1, relheight=1)
		self.bg.bind("<Enter>", self.enter)
		self.canvas.pack()
		self.mode = mode

	#Updates the GUI to reflect text mode
	def textMode(self):
		self.updateMode(Mode.TEXT)
	
	#Updates the GUI to reflect command mode
	def commandMode(self):
		self.updateMode(Mode.COMMAND)

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

	#Launch the GUI
	def start(self):
		self.root.mainloop()

	#Constructor for the GUI class
	#Initializes the Tkinter GUI object, binds the mouse hover event
	#and sets the object's properties
	def __init__(self):
		#Create the GUI object
		self.root = Tk()

		dir_path = os.path.dirname(os.path.realpath(__file__))
		#Load the images to use in the GUI
		if platform.system() == "Windows":
			self.commandImage = PhotoImage(file = dir_path + "\\assets\\command.gif")
			self.textImage = PhotoImage(file = dir_path + "\\assets\\text.gif")
		else:
			self.commandImage = PhotoImage(file = dir_path + "/assets/command.gif")
			self.textImage = PhotoImage(file = dir_path + "/assets/text.gif")

		#Set translucency
		self.root.wait_visibility(self.root)
		self.root.wm_attributes('-alpha',0.8)

		#Calculate screen size and get positions to move the window
		self.getPositions()

		#Move the GUI to the bottom left
		self.root.geometry(self.RIGHT + self.BOTTOM)
		self.right = True

		#Set the image to indicate command mode and set up window dimensions
		self.canvas = Canvas(self.root, bg="blue", height=50, width=100)
		self.commandMode()


if __name__ == "__main__":
	#Let us create a default GUI for testing
	tmp = GUIClass()
	tmp.start()
