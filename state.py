import log


import time
import re
import json
import struct
import sys
import win32gui, win32con, win32api, win32com

import keyboard
import pyautogui
import psutil
from keyboardEvent import KeyboardEvent
from window_properties import currentApp
import window_properties
from forwarder import encode_message, send_message

from voice import recalibrate
from word2number import w2n


def loadConfig():
    with open("config.cfg", "r") as f:
        s = f.read()
        config = json.loads(s)
    return config 

def saveConfig(config):
    with open("config.cfg", "w") as f:
        s = json.dumps(config)
        f.write(s)

class KeyboardMessage():
    def __init__(self, key, repeat=False, shiftKey=False, ctrlKey=False, altKey=False, metaKey=False):
        self.message = {
            'key': key,
            'repeat': repeat,
            'shiftKey': shiftKey,
            'ctrlKey': ctrlKey,
            'altKey': altKey,
            'metaKey': metaKey
        }

    def __json__(self):
        return self.message

browserKeywords = {
    'UP'             : [KeyboardMessage('k')],
    'DOWN'           : [KeyboardMessage('j')],
    'LEFT'           : [KeyboardMessage('h')],
    'RIGHT'          : [KeyboardMessage('l')],
    'CONTROL UP'     : [KeyboardMessage('u', ctrlKey=True)],
    'CONTROL DOWN'   : [KeyboardMessage('d', ctrlKey=True)],
    'CONTROL UPPER'  : [KeyboardMessage('b', ctrlKey=True)],
    'CONTROL DOWNER' : [KeyboardMessage('f', ctrlKey=True)],

    '0'              : [KeyboardMessage('0')],
    'ZERO'           : [KeyboardMessage('0')],
    'DOLLAR'         : [KeyboardMessage('$')],

    'TOP'            : [KeyboardMessage('g'), KeyboardMessage('g')],
    'BOTTOM'         : [KeyboardMessage('G', shiftKey=True)],

    'DELETE'         : [KeyboardMessage('d')],
    'UNDO'           : [KeyboardMessage('u')],
    'PREVIOUS'       : [KeyboardMessage('K', shiftKey=True)],
    'NEXT'           : [KeyboardMessage('J', shiftKey=True)],
    'REFRESH'        : [KeyboardMessage('r')],
    'DUPLICATE'      : [KeyboardMessage('z'), KeyboardMessage('d')],

    'FOLLOW'         : [KeyboardMessage('f')],
    'OPEN'           : [KeyboardMessage('F', shiftKey=True)],
    'BACK'           : [KeyboardMessage('H', shiftKey=True)],
    'FORWARD'        : [KeyboardMessage('L', shiftKey=True)],

    'ZOOM IN'        : [KeyboardMessage('z'), KeyboardMessage('i')],
    'ZOOM OUT'       : [KeyboardMessage('z'), KeyboardMessage('o')],
    'ZOOM DEFAULT'   : [KeyboardMessage('z'), KeyboardMessage('z')],

    'SEARCH'         : [KeyboardMessage('k', ctrlKey=True)],
    'FIND'           : [KeyboardMessage('f', ctrlKey=True)],
    'ADDRESS'        : [KeyboardMessage('l', ctrlKey=True)],
    'NEW TAB'        : [KeyboardMessage('z'), KeyboardMessage('d')],
    'NEW WINDOW'     : [KeyboardMessage('n', ctrlKey=True)],
    'PRINT'          : [KeyboardMessage('p', ctrlKey=True)],
    'SAVE'           : [KeyboardMessage('s', ctrlKey=True)],

}

wordKeywords = {
    "NAVIGATE" : {
        'UP'    : 'up',
        'DOWN'  : 'down',
        'PARAGRAPH UP': 'ctrl+up',
        'PARAGRAPH DOWN': 'ctrl+down',
        'PAGE UP': 'ctrl+page up',
        'PAGE DOWN': 'ctrl+page down',
        'LEFT'  : 'ctrl+left',
        'RIGHT' : 'ctrl+right',
        'PERIOD': '.',
        'COMMA': ',',
        'EXCLAMATION': '!',
        'QUESTION': '?',
        'SLASH': '/',
        'COLON': ':',
        'SEMICOLON': ';',
        'APOSTROPHE': '\'',
        'QUOTE': '\"',
        'OPEN PARENTHESIS': '(',
        'CLOSE PARENTHESIS': ')',
        'AMPERSAND': '&',
        'DOLLAR': '$',
        'STAR': '*',
        'LEFT ALIGN': 'ctrl+l',
        'CENTER ALIGN': 'ctrl+e',
        'RIGHT ALIGN': 'ctrl+r',
        'UNDO': 'ctrl+z',
        'RE DO': 'ctrl+y',
        'INDENT': 'tab',
        'REMOVE INDENT': 'shift+tab',
    },

    "HIGHLIGHT" : {
        'DOWN': 'ctrl+shift+down',
        'UP': 'ctrl+shift+up',
        'RIGHT': 'ctrl+shift+right',
        'LEFT': 'ctrl+shift+left',
        'BOLD': 'ctrl+b',
        'ITALICS': 'ctrl+i',
        'UNDERLINE': 'ctrl+u',
        'DELETE': 'backspace',
        'ALL': 'ctrl+a',
        'INCREASE SIZE': 'ctrl+]',
        'DECREASE SIZE': 'ctrl+[',
        'CAPS': 'shift+F3', # rotates between 'this', 'This' and 'THIS'
    }
}


class state:
    def __init__(self, g):
        # Define bits for modes we can be in
        self.NORMAL     = 2**0
        self.HOLDING    = 2**1
        self.FOLLOW     = 2**2  # Hacky meta-method to accept letters
        self.INSERT     = 2**3
        self.SETTINGS   = 2**4
        self.RECORDING  = 2**5
        self.CLEAR      = 0

        self.mode = self.NORMAL
        self.wordMode = "NAVIGATE"

        #0 = not recording
        #1 = recording
        #2 = naming
        #3 = confirming
        self.recordingStatus = 0
        self.macroName = None
        self.macroCommands = []

        self.gui = g
        self.held = set()

        #Load the configuration file into a dictionary
        try:
            self.config = loadConfig()
        except FileNotFoundError:
            # FIXME: handle case where there is no config file
            log.error("No config file found! Ignoring error for now...")
            self.config = {} 
            self.config['macros'] = {}

        self.commands = {
            "ALT": self.parseAlt,
            "HOLD": self.parseHold,
            "RESIZE": self.parseResize,
            "ESCAPE": self.parseEscape,
            "HELP": self.parseHelp,
            "SETTINGS": self.parseSettings,
            "LAUNCH": self.parseLaunch,
            "SWITCH": self.parseSwitch,
            "MOVE": self.gui.enter, #Moves the GUI out of the way
            "RECORD": self.parseRecord,
            "TYPE":  self.parseKeystroke,
            "FOCUS": self.parseFocus,
            "MINIMIZE": self.parseMinimize,
            "MAXIMIZE": self.parseMaximize,
            "SNAP": self.parseSnap,
            "UNSNAP": self.parseUnsnap,
            "CANCEL": self.parseCancel
        }


    def switchMode(self):
        log.info("Switching modes")
        if self.mode & self.NORMAL:
            self.mode = self.INSERT
            self.gui.setMode(self.mode)
        else:
            self.mode = self.NORMAL
            self.gui.setMode(self.mode)


    def parseAlt(self, tokens):
        if len(tokens) > 1 and tokens[0] == 'TAB':
            KeyboardEvent.pressSequence(['ALT', 'TAB'])
        else:
            msg = "No parameter" if len(tokens) == 0 else tokens[0]
            log.parse_error(log.ParseError.ALT, msg)

        self.parseImpl(tokens[1:])


    def parseHold(self, tokens):
        def clearHeld():
            self.mode &= ~self.HOLDING
            for key in self.held:
                KeyboardEvent.keyUp(key)
                self.gui.removeHold(key)

        self.mode |= self.HOLDING
        for token in tokens:
            if token == 'ESCAPE':
                clearHeld()
                self.parseImpl(tokens[tokens.index(token)+1:])
                return

            if KeyboardEvent.keyDown(token):
                self.held.add(token)
                self.gui.addHold(token)
            else:
                log.parse_error(log.ParseError.HOLD, token)
                clearHeld()
                return


    def parseResize(self, tokens):
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)

        half_width = screen_width // 2
        half_height = screen_height // 2

        fg_hwnd = win32gui.GetForegroundWindow()
        def resize(x, y, w, h):
            win32gui.MoveWindow(fg_hwnd, x, y, w, h, True)

        if len(tokens) == 0:
            log.parse_error(log.ParseError.RESIZE, "No parameter")
        elif tokens[0] == 'LEFT':
            resize(0, 0, half_width, screen_height)
        elif tokens[0] == 'RIGHT':
            resize(half_width + 1, 0, half_width, screen_height)
        elif tokens[0] == 'UP':
            resize(0, 0, screen_width, half_height)
        elif tokens[0] == 'DOWN':
            resize(0, half_height + 1, screen_width, half_height)
        elif tokens[0] == 'FULL':
            resize(0, 0, screen_width, screen_height)
        else:
            log.parse_error(log.ParseError.RESIZE, tokens[0])

        self.parseImpl(tokens[1:])


    def parseEscape(self, tokens):
        self.switchMode()
        self.parseImpl(tokens)

    def parseHelp(self,tokens):
        if len(tokens) == 0:
            self.gui.helpMode()
        elif tokens[0] == 'BROWSER':
            self.gui.helpMode('browser')
        elif tokens[0] == 'CLOSE':
            self.gui.closeHelpMenu()
        else:
            log.parse_error(log.ParseError.HELP, tokens[0])

    def parseSettings(self,tokens):
        if len(tokens) == 0:
            self.gui.settingsMode()
        elif tokens[0] == 'CALIBRATE':
            recalibrate()
        elif tokens[0] == 'MACRO':
            self.gui.settingsMode("MACRO")
        elif tokens[0] == 'ALIAS':
            self.gui.settingsMode("ALIAS")
        elif tokens[0] == 'CLOSE':
            self.gui.closeSettings()
        else:
            log.Logger.log(log.ParseError.HELP, tokens[0])

    def parseLaunch(self, tokens):
        """TODO:
            Launch applications via Windows functionality.
            Either Win -> Application name or using run?
            Token will likely be the name of the application
        """
        self.gui.showError("Not yet\nimplemented")
    
    def parseSwitch(self, tokens):
        keyboard.press_and_release("alt+tab")

    def parseFocus(self, tokens):
        # https://stackoverflow.com/questions/44735798/pywin32-how-to-get-window-handle-from-process-handle-and-vice-versa

        log.debug("app to focus: '{}'".format(tokens[0]))
        if len(tokens) != 1:
            self.gui.showError("Incorrect\nusage of focus")
            log.warn("focus used without exactly one token")
            return


        process_name = None
        if tokens[0] == 'WORD':
            process_name = 'WINWORD.EXE'
        else:
            process_name = tokens[0].lower() + '.exe'

        handles = window_properties.getMainWindowHandles(process_name, expect_one=True)
        if not handles:
            self.gui.showError("No app to focus")
            return

        # NOTE: we choose an arbitrary handle if there's more than one
        handle = handles[0]

        for ntries in range(3):
            try:
                win32gui.SetForegroundWindow(handle)
                break
            except Exception:
                time.sleep(1) # hopefully the error was temporary?
        else:
            log.error("couldn't focus app '{}'".format(tokens[0]))
            self.gui.showError("Couldn't focus app")
            return

        # Display the window normally (i.e. not minimized/maximized)
        win32gui.ShowWindow(handle, win32con.SW_SHOWNORMAL)

    def parseMaximize(self, tokens):

        if tokens:
            self.gui.showError("Incorrect\nusage of maximize")

        handle = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(handle, win32con.SW_MAXIMIZE)


    def parseMinimize(self, tokens):
        if tokens:
            self.gui.showError("Incorrect\nusage of minimize")

        handle = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(handle, win32con.SW_MINIMIZE)

    def parseSnap(self, tokens):
        if len(tokens) != 1:
            self.gui.showError("Incorrect\nusage")
            log.warn("exactly one token required for snap. {} found".format(len(tokens)))
            return

        self.parseUnsnap([])

        # escape is needed to cancel another shortcut that activates inadvertently
        snap_type = tokens[0]
        if snap_type == 'LEFT':
            pyautogui.hotkey('win', 'left', 'escape')
            time.sleep(1)
        elif snap_type == 'RIGHT':
            pyautogui.hotkey('win', 'right', 'escape')
            time.sleep(1)
        else:
            self.gui.showError("Invalid\nsnap type")
            log.warn("invalid snap type")


    def parseUnsnap(self, tokens):
        if tokens:
            self.gui.showError("Incorrect\nusage")
            log.warn("Expected 0 tokens for unsnap")
            return

        handle = win32gui.GetForegroundWindow()
        win32gui.ShowWindow(handle, win32con.SW_NORMAL)

    def parseCancel(self, tokens):
        """Remove all follow pop-ups and leave follow mode"""

        # NOTE: this could be extended to exit insert mode, etc.
        pyautogui.hotkey('escape')
        self.mode &= ~self.FOLLOW

    def parseRecord(self, tokens):
        """TODO:
            Add ability to record macros.
            Tokens could be "Start" or "End" with the macro commands
            Sandwiched between "Record start" and "record end"
        """
        pass

    def parseKeystroke(self, tokens):
        if len(tokens) == 1:
            keyboard.press_and_release(tokens[0])
        else:
            log.Logger.log(log.ParseError.TYPE, tokens)

    def executeSearch(self, tokens):
        """TODO:
            Add ability to search in one command.
            Tokens should be the search term.
            This effectively accomplishes:
                ctrl+k (go to search bar),
                entering tokens as text,
                alt+enter (open in new tab),
        """
        keyboard.press_and_release('ctrl+k')
        time.sleep(1)
        keyboard.write(' '.join(tokens).capitalize())
        time.sleep(0.25)

        time.sleep(1)
        keyboard.press_and_release('alt+enter')

    def forwardWord(self, tokens):
        tokenStr = ' '.join(tokens)
        if tokenStr in ["INSERT", "NAVIGATE", "HIGHLIGHT"]:
            self.wordMode = tokenStr
            return

        if self.wordMode == "INSERT":
            keyboard.write(tokenStr.lower())
            return

        elif tokenStr in wordKeywords[self.wordMode]:
            keyboard.press_and_release(wordKeywords[self.wordMode][tokenStr])
            return

        #This is because we support "down X" where x is arbitrary
        elif tokens[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
            try:
                num = w2n.word_to_num(tokens[1:])
            except Exception as e:
                raise Exception("Navigate (U/D/L/R) did not receive a number arg")
            for i in range(num):
                keyboard.press_and_release(wordKeywords[self.wordMode][tokens[0]])
                time.sleep(.1)




    def forwardBrowser(self, tokens):
        tokenStr = ' '.join(tokens)
        if tokenStr in browserKeywords:
            # Hacky interception of next few chars to send with follow
            if tokenStr == 'FOLLOW' or tokenStr == 'OPEN':
                self.mode |= self.FOLLOW
            send_message(encode_message(browserKeywords[tokenStr]))

        elif tokens[0] == 'SEARCH':
                self.executeSearch(tokens[1:])
        elif len(tokens) > 1 and tokens[0] == "NEW" and tokens[1] == "TAB":
            keyboard.press_and_release("ctrl+t")
        else:
            log.parse_error(log.ParseError.BROWSER, tokenStr)


    def parseImpl(self, tokens, levelDict = None):
        if not tokens:
            return

        if self.mode & self.HOLDING:
            self.parseHold(tokens)
            return

        # TODO: better method of accepting letters to follow
        #   currently just takes all tokens as individual letters and sends
        #   them on assuming that there's no point in issuing commands
        #   before the link is followed. Also, there should not be more than 3
        if self.mode & self.FOLLOW:
            # handle switch specially so that alt-tabbing works with the prompt
            if tokens[0] == 'SWITCH' and len(tokens) == 1:
                self.parseSwitch(tokens[1:])
                return
            elif tokens[0] == 'CANCEL' and len(tokens) == 1:
                self.parseCancel([])
                return

            self.mode &= ~self.FOLLOW

            if len(tokens) > 3:
                log.warn("cannot handle more than 3 follow characters")
                return
            for token in tokens:
                if len(token) != 1:
                    log.warn("cannot handle follow token size greater than 1")
                    return

            enumerated_keys = [KeyboardMessage(tok) for tok in tokens]
            send_message(encode_message(enumerated_keys))

            return

        if levelDict == None:
            levelDict = self.commands

        w, rest = tokens[0], tokens[1:]
        # debug(w)
        # debug(levelDict)
        if w in levelDict:
            if isinstance(levelDict[w], dict):
                self.parseImpl(rest, levelDict[w])
            else:
                #Calls the function at levelDict[w] with args([rest])
                levelDict[w](rest)
        else:
            log.debug('current app: ', currentApp())
            if currentApp() == 'Firefox':
                self.forwardBrowser(tokens)
            elif currentApp() == 'Microsoft Word':
                self.forwardWord(tokens)
            else:
                self.gui.showError("Unrecognized\nCommand")
                log.warn("Command not found")


    def parse(self, command):
        self.ready = False
        log.debug('parse: command: ', command)
        command = command.strip().upper()

        #Handle recording commands here so we can return immediately after
        if self.recordingStatus == 0: #Not recording
            if command == "RECORD START":
                self.gui.startRecording()
                self.macroCommands = []
                self.recordingStatus = 1
                return
        elif self.recordingStatus == 1: #Recording
            if command == "RECORD END":
                self.gui.endRecording()
                self.recordingStatus = 2
                return
        elif self.recordingStatus == 2: #Naming
            self.macroName = command
            self.gui.macroNameEntered(command)
            self.recordingStatus = 3
            return
        elif self.recordingStatus == 3: #Confirming
            if command.strip().upper() == "YES":
                self.config['macros'][self.macroName] = self.macroCommands
                saveConfig(self.config)
                self.gui.macroNameConfirmed()
                self.recordingStatus = 0
                return
            elif command.strip().upper() == "NO":
                self.gui.endRecording()
                self.recordingStatus = 2
                return
            else:
                raise ValueError("Please answer\nyes or no")

        if len(command) == 1:
            command = command.lower()
        if self.mode & self.NORMAL:
            command = re.sub('[!@#$\']', '', command)
            text = re.findall(r"[a-zA-Z]+", command)
            log.info("Tokens parsed: {}".format(text))

            self.parseImpl(text)
        elif self.mode & self.INSERT:
            #
            # Only use these meta-commands if they're by themselves.
            # 'ESCAPE' = Exit insert mode
            if command == 'ESCAPE':
                self.switchMode()
            
            # 'ENTER' = Send the Enter key
            # Might want to consider having this implicitly exit insert mode?
            elif command == 'ENTER':
                keyboard.press_and_release('enter')
            else:
                log.info("Sending: \"{}\" to top application".format(command))
                keyboard.write(command)
                #keys = [KeyboardMessage(ch) for ch in command]
                #send_message(encode_message(keys))

        else:
            raise ValueError('Unknown mode in parser!')


        #If we are recording and the command parsed successfully, store it
        if self.recordingStatus == 1:
            self.macroCommands.append(command)
        
        # sleep after parsing to allow commands to send appropriately
        time.sleep(0.5)

    #Returns a list of options available to the user, using the given text file
    def parseMenu(filename):
        with open(filename) as f:
            lines = f.readlines()
        
        commandList = []
        for line in f:
            if isnumber(line[0]) and line[1] == '.':
                commandList.append(line)
        
        return commandList

# v.parse("hold alt")
# time.sleep(2)
# v.parse("tab")
# # v.parse("tab")
# v.parse("escape")
# v.parse("zoom in")
# v.parse("follow")
# v.parse("a a")
# v.parse("address")
# v.parse("resize left")
# time.sleep(0.75)
# v.parse("resize right")
# time.sleep(0.75)
# v.parse("resize up")
# time.sleep(0.75)
# v.parse("resize down")
# time.sleep(0.75)
# v.parse("resize full")
