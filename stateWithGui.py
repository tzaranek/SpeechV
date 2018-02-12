import time
import re
import json
import struct
import sys
import win32gui, win32con, win32api

from keyboard import KeyboardEvent
from window_properties import currentApp
import error

class EncoderOverload(json.JSONEncoder):
    """
    JSONEncoder subclass that leverages an object's `__json__()` method,
    if available, to obtain its default JSON representation. 

    """
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)


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
    'UP'             : KeyboardMessage('j'),
    'DOWN'           : KeyboardMessage('k'),
    'LEFT'           : KeyboardMessage('h'),
    'RIGHT'          : KeyboardMessage('l'),
    'CONTROL UP'     : KeyboardMessage('u', ctrlKey=True),
    'CONTROL DOWN'   : KeyboardMessage('d', ctrlKey=True),
    'CONTROL UPPER'  : KeyboardMessage('b', ctrlKey=True),
    'CONTROL DOWNER' : KeyboardMessage('f', ctrlKey=True),

    '0'              : KeyboardMessage('0'),
    'ZERO'           : KeyboardMessage('0'),
    'DOLLAR'         : KeyboardMessage('$'),

    'TOP'            : KeyboardMessage('gg'),
    'BOTTOM'         : KeyboardMessage('G'),

    'DELETE'         : KeyboardMessage('d'),
    'UNDO'           : KeyboardMessage('u'),
    'PREVIOUS'       : KeyboardMessage('K'),
    'NEXT'           : KeyboardMessage('J'),
    'REFRESH'        : KeyboardMessage('r'),
    'DUPLICATE'      : KeyboardMessage('zd'),

    'FOLLOW'         : KeyboardMessage('f'),
    'OPEN'           : KeyboardMessage('F'),
    'BACK'           : KeyboardMessage('H'),
    'FORWARD'        : KeyboardMessage('L'),

    'ZOOM IN'        : KeyboardMessage('zi'),
    'ZOOM OUT'       : KeyboardMessage('zo'),
    'ZOOM DEFAULT'   : KeyboardMessage('zd'),

    'FIND'           : KeyboardMessage('f', ctrlKey=True),
    'ADDRESS'        : KeyboardMessage('l', ctrlKey=True),
    'NEW TAB'        : KeyboardMessage('t', ctrlKey=True),
    'NEW WINDOW'     : KeyboardMessage('n', ctrlKey=True),
    'PRINT'          : KeyboardMessage('p', ctrlKey=True),
    'SAVE'           : KeyboardMessage('s', ctrlKey=True),
}

# source: https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Native_messaging
def encode_message(message_content):
    encoded_content = json.dumps(message_content, cls=EncoderOverload)
    encoded_length = struct.pack('@I', len(encoded_content))
    return {'length': encoded_length, 'content': encoded_content}


# source: https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Native_messaging
def send_message(encoded_message):
    try:
        # python 2.7 compatible - supported because firefox insists on using v2
        sys.stdout.write(encoded_message['length'])
        sys.stdout.write(encoded_message['content'].encode())
        sys.stdout.flush()
    except TypeError:
        # python 3 compatible
        sys.stdout.buffer.write(encoded_message['length'])
        sys.stdout.buffer.write(encoded_message['content'].encode())
        sys.stdout.flush()


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


    def switchMode(self):
        print("Switching modes")
        self.mode = self.INSERT if self.mode & self.NORMAL else self.NORMAL


    def parseAlt(self, tokens):
        if tokens[0] == 'TAB':
            KeyboardEvent.pressSequence(['ALT', 'TAB'])
        else:
            error.Logger.log(error.ParseError.ALT, tokens[0])

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
                error.Logger.log(error.ParseError.HOLD, token)
                clearHeld()
                self.parseImpl(tokens[tokens.index(token)+1:])
                return


    def parseResize(self, tokens):
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)

        half_width = screen_width // 2
        half_height = screen_height // 2

        fg_hwnd = win32gui.GetForegroundWindow()
        def resize(x, y, w, h):
            win32gui.MoveWindow(fg_hwnd, x, y, w, h, True)

        if tokens[0] == 'LEFT':
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
            error.Logger.log(error.ParseError.RESIZE, tokens[0])

        self.parseImpl(tokens[1:])


    def parseEscape(self, tokens):
        self.switchMode()
        self.parseImpl(tokens)

    def parseHelp(self,tokens):
        if tokens[0] is None:
            self.gui.helpMode()
        elif tokens[1] == 'BROWSER':
            self.gui.helpMode('browser')
        elif tokens[2] == 'CLOSE':
            self.gui.closeHelpMenu()
        else:
            error.Logger.log(error.ParseError.HELP, tokens[0])


    def forwardBrowser(self, tokens):
        tokenStr = ' '.join(tokens)
        if tokenStr in browserKeywords:
            # Hacky interception of next few chars to send with follow
            if tokenStr == 'FOLLOW':
                self.mode |= self.FOLLOW
            send_message(encode_message(browserKeywords[tokenStr]))
        else:
            error.Logger.log(error.ParseError.BROWSER, tokenStr)


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
                print("OOPS")
                return
            for token in tokens:
                if len(token) != 1:
                    print("OOPS")
                    return

            for token in tokens:
                send_message(encode_message(KeyboardMessage(token)))

            return

        if levelDict == None:
            levelDict = self.commands

        w, rest = tokens[0], tokens[1:]
        print(w)
        print(levelDict)
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
                print("Command not found")


    def parse(self, command):
        command = command.strip().upper()
        if self.mode & self.NORMAL:
            text = re.findall(r"[a-zA-Z]+", command)
            print("Tokens parsed: {}".format(text))

            self.parseImpl(text)
        else:
            if command == "caps lock":
                self.switchMode(command)
            else:
                print("Sending: \"{}\" to top application".format(command))

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
