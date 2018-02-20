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

def or_seq(lst):
    msk = 0
    for num in lst:
        msk |= num
    return msk


browserKeywords = {
    'UP'             : [KeyboardMessage('j')],
    'DOWN'           : [KeyboardMessage('k')],
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
    'BOTTOM'         : [KeyboardMessage('G')],

    'DELETE'         : [KeyboardMessage('d')],
    'UNDO'           : [KeyboardMessage('u')],
    'PREVIOUS'       : [KeyboardMessage('K')],
    'NEXT'           : [KeyboardMessage('J')],
    'REFRESH'        : [KeyboardMessage('r')],
    'DUPLICATE'      : [KeyboardMessage('z'), KeyboardMessage('d')],

    'FOLLOW'         : [KeyboardMessage('f')],
    'OPEN'           : [KeyboardMessage('F')],
    'BACK'           : [KeyboardMessage('H')],
    'FORWARD'        : [KeyboardMessage('L')],

    'ZOOM IN'        : [KeyboardMessage('z'), KeyboardMessage('i')],
    'ZOOM OUT'       : [KeyboardMessage('z'), KeyboardMessage('o')],
    'ZOOM DEFAULT'   : [KeyboardMessage('z'), KeyboardMessage('d')],

    'FIND'           : [KeyboardMessage('f', ctrlKey=True)],
    'ADDRESS'        : [KeyboardMessage('l', ctrlKey=True)],
    'NEW TAB'        : [KeyboardMessage('t', ctrlKey=True)],
    'NEW WINDOW'     : [KeyboardMessage('n', ctrlKey=True)],
    'PRINT'          : [KeyboardMessage('p', ctrlKey=True)],
    'SAVE'           : [KeyboardMessage('s', ctrlKey=True)],
}


class state:
    def __init__(self, g):
        # Define bits for modes we can be in
        self.NORMAL     = 2**0
        self.HOLDING    = 2**1
        self.FOLLOW     = 2**2  # Hacky meta-method to accept letters
        self.INSERT     = 2**3
        self.CLEAR      = 0

        self.mode = self.NORMAL
        self.gui = g
        self.held = set()

        self.commands = {
            "ALT": self.parseAlt,
            "HOLD": self.parseHold,
            "RESIZE": self.parseResize,
            "ESCAPE": self.parseEscape,
            "HELP": self.parseHelp
        }



    def inMode(self, *modes):
        return self.mode & or_seq(modes)


    def setMode(self, *modes):
        self.mode |= or_seq(modes)


    def clearMode(self, *modes):
        # TODO: check that bitwise complement works as expected in python
        self.mode &= ~or_seq(modes)


    def switchMode(self):
        log.info("Switching modes")
        if self.inMode(self.NORMAL):
            self.mode = self.INSERT
            self.gui.setMode(gui.Mode.TEXT)
        else:
            self.mode = self.NORMAL
            self.gui.setMode(gui.Mode.COMMAND)


    def parseAlt(self, tokens):
        if len(tokens) > 0 and tokens[0] == 'TAB':
            KeyboardEvent.pressSequence(['ALT', 'TAB'])
        else:
            msg = "No parameter" if len(tokens) == 0 else tokens[0]
            log.parse_error(log.ParseError.ALT, msg)

        self.parseImpl(tokens[1:])


    def parseHold(self, tokens):
        def clearHeld():
            self.clearMode(self.HOLDING)
            for key in self.held:
                KeyboardEvent.keyUp(key)
                self.gui.removeHold(key)
            self.held = set()

        self.setMode(self.HOLDING)
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


    def forwardBrowser(self, tokens):
        tokenStr = ' '.join(tokens)
        if tokenStr in browserKeywords:
            # Hacky interception of next few chars to send with follow
            if tokenStr == 'FOLLOW':
                self.setMode(self.FOLLOW)
            send_message(encode_message(browserKeywords[tokenStr]))
        else:
            log.parse_error(log.ParseError.BROWSER, tokenStr)


    def parseImpl(self, tokens, levelDict = None):
        if not tokens:
            return

        if self.inMode(self.HOLDING):
            self.parseHold(tokens)
            return

        # TODO: better method of accepting letters to follow
        #   currently just takes all tokens as individual letters and sends
        #   them on assuming that there's no point in issuing commands
        #   before the link is followed. Also, there should not be more than 3
        if self.inMode(self.FOLLOW):
            self.clearMode(self.FOLLOW)

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
                levelDict[w](rest)
        else:
            if currentApp() == 'Firefox':
                self.forwardBrowser(tokens)
            else:
                self.gui.showError()
                log.warn("Command not found")


    def parse(self, command):
        command = command.strip().upper()
        if len(command) == 1:
            command = command.lower()
        if self.inMode(self.NORMAL):
            text = re.findall(r"[a-zA-Z]+", command)
            log.info("Tokens parsed: {}".format(text))

            self.parseImpl(text)
        else:
            # Only switch back to normal mode if the *entire* command is
            # 'ESCAPE'
            if command == 'ESCAPE':
                self.switchMode()
            else:
                log.info("Sending: \"{}\" to top application".format(command))
                keyboard.write(command)
                #keys = [KeyboardMessage(ch) for ch in command]
                #send_message(encode_message(keys))


        # sleep after parsing to allow commands to send appropriately
        time.sleep(0.25)

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
