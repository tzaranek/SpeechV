import time
import re
import json
import struct
import sys
import win32gui, win32con, win32api

import keyboard
from keyboardEvent import KeyboardEvent
from window_properties import currentApp
import log
from forwarder import encode_message, send_message

from voice import recalibrate


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
    navigate = {
        'UP'    : keyboard.press_and_release('up'),
        'DOWN'  : keyboard.press_and_release('down'),
        'PARAGRAPH UP': keyboard.press_and_release('ctrl+up'),
        'PARAGRAPH DOWN': keyboard.press_and_release('ctrl+down'),
        'PAGE UP': keyboard.press_and_release('ctrl+page up'),
        'PAGE DOWN': keyboard.press_and_release('ctrl+page down'),
        'LEFT'  : keyboard.press_and_release('ctrl+left'),
        'RIGHT' : keyboard.press_and_release('ctrl+right'),
        'PERIOD': keyboard.press_and_release('.'),
        'COMMA': keyboard.press_and_release(','),
        'EXCLAMATION': keyboard.press_and_release('!'),
        'QUESTION': keyboard.press_and_release('?'),
        'SLASH': keyboard.press_and_release('/'),
        'COLON': keyboard.press_and_release(':'),
        'SEMICOLON': keyboard.press_and_release(';'),
        'APOSTROPHE': keyboard.press_and_release('\''),
        'QUOTE': keyboard.press_and_release('\"'),
        'OPEN PARENTHESIS': keyboard.press_and_release('('),
        'CLOSE PARENTHESIS': keyboard.press_and_release(')'),
        'AMPERSAND': keyboard.press_and_release('&'),
        'DOLLAR': keyboard.press_and_release('$'),
        'STAR': keyboard.press_and_release('*'),
        'LEFT ALIGN': keyboard.press_and_release('ctrl+l'),
        'CENTER ALIGN': keyboard.press_and_release('ctrl+e'),
        'RIGHT ALIGN': keyboard.press_and_release('ctrl+r'),
        'UNDO': keyboard.press_and_release('ctrl+z'),
        'RE DO': keyboard.press_and_release('ctrl+y')
    },

    highlight = {
        'DOWN': keyboard.press_and_release('ctrl+shift+down'),
        'UP': keyboard.press_and_release('ctrl+shift+up'),
        'RIGHT': keyboard.press_and_release('ctrl+shift+right'),
        'LEFT': keyboard.press_and_release('ctrl+shift+left'),
        'BOLD': keyboard.press_and_release('ctrl+b'),
        'ITALICS': keyboard.press_and_release('ctrl+i'),
        'UNDERLINE': keyboard.press_and_release('ctrl+u'),
        'DELETE': keyboard.press_and_release('backspace'),
        'ALL': keyboard.press_and_release('ctrl+a'),
        'INCREASE SIZE': keyboard.press_and_relase('ctrl+]'),
        'DECREASE SIZE': keyboard.press_and_release('ctrl+['),
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
        self.CLEAR      = 0

        self.mode = self.NORMAL
        self.gui = g
        self.held = set()

        self.commands = {
            "ALT": self.parseAlt,
            "HOLD": self.parseHold,
            "RESIZE": self.parseResize,
            "ESCAPE": self.parseEscape,
            "HELP": self.parseHelp,
            "SETTINGS": self.parseSettings,
            "LAUNCH": self.parseLaunch,
            "SWITCH": self.parseSwitch,
            "FOCUS": self.parseFocus,
            "MOVE": self.gui.enter, #Moves the GUI out of the way
            "RECORD": self.parseRecord
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
        assert(self.mode == self.NORMAL)
        keyboard.press_and_release("alt+tab")

    def parseFocus(self, tokens):
        """TODO:
            Create a macro to perform one or more alt tabs
            Token should be the name of the application we want to switch to
            Then, this function can alt tab up to active applications - 1 times
            and compare currentApp() with the target application and stop
        """
        while currentApp() != "Microsoft Word":
            self.parseSwitch("Test")
        self.gui.showError("Not yet\nimplemented\nDemo Hardcode")
    
    def parseRecord(self, tokens):
        """TODO:
            Add ability to record macros.
            Tokens could be "Start" or "End" with the macro commands
            Sandwiched between "Record start" and "record end"
        """
        self.gui.showError("Not yet\nimplemented")

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
            self.mode &= ~self.FOLLOW

            if len(tokens) > 3:
                log.debug("OOPS")
                return
            for token in tokens:
                if len(token) != 1:
                    log.debug("OOPS")
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
            if currentApp() == 'Firefox':
                self.forwardBrowser(tokens)
            else:
                self.gui.showError("Unrecognized\nCommand")
                log.warn("Command not found")


    def parse(self, command):
        self.ready = False
        command = command.strip().upper()
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

# v = state()
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
