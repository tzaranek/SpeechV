import time
import re
import json
import struct
import sys
import win32gui, win32con, win32api
from keyboard import KeyboardEvent
from window_properties import currentApp

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
    def __init__(self):
        # Define bits for modes we can be in
        self.NORMAL     = 2**0
        self.HOLDING    = 2**1
        self.INSERT     = 2**2
        self.CLEAR      = 0

        self.mode = self.NORMAL

        self.held = set()

        self.commands = {
            "ALT": self.parseAlt,
            "HOLD": self.parseHold,
            "RESIZE": self.parseResize,
            "ESCAPE": self.parseEscape
        }


    def switchMode(self):
        print("Switching modes")
        self.mode = self.INSERT if self.mode & self.NORMAL else self.NORMAL


    def parseAlt(self, tokens):
        if tokens[0] == 'TAB':
            KeyboardEvent.pressSequence(['ALT', 'TAB'])
        else:
            print("Parsing ALT command failed. Could not recognize: {}".format(tokens[0]))

        self.recursiveParse(tokens[1:])


    def parseHold(self, tokens):
        def clearHeld():
            self.mode &= ~self.HOLDING
            for key in self.held:
                KeyboardEvent.keyUp(key)

        self.mode |= self.HOLDING
        for token in tokens:
            if token == 'ESCAPE':
                clearHeld()
                self.recursiveParse(tokens[tokens.index(token)+1:])
                return

            if KeyboardEvent.keyDown(token):
                self.held.add(token)
            else:
                print("Parsing HOLD command failed. Could not recognize: {}".format(token))
                clearHeld()
                self.recursiveParse(tokens[tokens.index(token)+1:])
                return


    def parseResize(self, tokens):
        if tokens[0] == 'LEFT':
            pass
        elif tokens[0] == 'RIGHT':
            pass
        elif tokens[0] == 'UP':
            pass
        elif tokens[0] == 'DOWN':
            pass
        elif tokens[0] == 'FULL':
            pass
        else:
            print("Parsing RESIZE command failed. Could not recognize: {}".format(tokens[0]))

        self.recursiveParse(tokens[1:])


    def parseEscape(self, tokens):
        self.switchMode()
        self.recursiveParse(tokens)


    def forwardBrowser(self, tokens):
        tokenStr = ' '.join(tokens)
        if tokenStr in browserKeywords:
            send_message(encode_message(browserKeywords[tokenStr]))


    def recursiveParse(self, tokens, levelDict = None):
        if not tokens:
            return

        if self.mode & self.HOLDING:
            self.parseHold(tokens)
            return

        if levelDict == None:
            levelDict = self.commands

        w, rest = tokens[0], tokens[1:]
        if w in levelDict:
            if isinstance(levelDict[w], dict):
                self.recursiveParse(rest, levelDict[w])
            else:
                levelDict[w](rest)
        else:
            # TODO: change this for testing w/ firefox
            if currentApp() == 'Google Chrome':
                self.forwardBrowser(tokens)
            else:
                print("Command not found")


    def parse(self, command):
        command = command.strip().upper()
        if self.mode & self.NORMAL:
            text = re.findall(r"[a-zA-Z]+", command)
            print("Tokens parsed: {}".format(text))

            self.recursiveParse(text)
        else:
            if command == "caps lock":
                self.switchMode(command)
            else:
                print("Sending: \"{}\" to top application".format(command))

v = state()
v.parse("alt tab")
v.parse("hold alt")
time.sleep(1)
v.parse("tab")
time.sleep(1)
v.parse("tab")
time.sleep(1)
v.parse("escape")
v.parse("control up")
