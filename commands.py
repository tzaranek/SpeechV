import log


import time
import re
import json
import struct
import sys
from enum import Enum


import win32gui, win32con, win32api, win32com
import keyboard
import pyautogui
import psutil
from keyboardEvent import KeyboardEvent
from word2number import w2n


import window_properties
from window_properties import currentApp
from forwarder import encode_message, send_message
from globs import gui
from mode import *


try:
    from voice import recalibrate, adjustTimeout
except ImportError:
    log.error("FAILED TO IMPORT VOICE")
    pass # FIXME: ignore circular import 

class KeyboardMessage():
    """Format for keyboard messages sent to our custom firefox extension"""
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


def exeAlt(tokens, mode):
    if len(tokens) > 1 and tokens[0] == 'TAB':
        KeyboardEvent.pressSequence(['ALT', 'TAB'])
    else:
        msg = "No parameter" if len(tokens) == 0 else tokens[0]
        log.parse_error(log.ParseError.ALT, msg)

    return (self.parseImpl(tokens[1:], mode))


def exeResize(tokens, mode):
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

    return (tokens[1:], mode)

def exeClose(tokens, mode):
    pass

def exeHelp(tokens, mode):
    if len(tokens) == 0:
        gui.helpMode()
    elif tokens[0] == 'BROWSER':
        gui.helpMode('browser')
    elif tokens[0] == 'CLOSE':
        gui.closeHelpMenu()
    else:
        log.parse_error(log.ParseError.HELP, tokens[0])

def exeSettings(tokens, mode):
    if len(tokens) == 0:
        gui.settingsMode()
    elif tokens[0] == 'CALIBRATE':
        recalibrate()
    #Need to fix circular dependency in order to do this
    elif tokens[0] == 'TIMEOUT':
        pass
        adjustTimeout(tokens[1:])
    elif len(tokens) > 1 and tokens[0] == 'TIME' and tokens[1] == 'OUT':
        pass
        adjustTimeout(tokens[2:])
    elif tokens[0] == 'MACRO':
        gui.settingsMode("MACRO")
    elif tokens[0] == 'ALIAS':
        gui.settingsMode("ALIAS")
    elif tokens[0] == 'CLOSE':
        gui.closeSettings()
    elif tokens[0] == 'RESIZE':
        gui.resizeWindow(tokens[1:])
    else:
        log.Logger.log(log.ParseError.HELP, tokens[0])

def exeLaunch(tokens, mode):
    """TODO:
        Launch applications via Windows functionality.
        Either Win -> Application name or using run?
        Token will likely be the name of the application
    """
    gui.showError("Not yet\nimplemented")

def exeSwitch(tokens, mode):
    keyboard.press_and_release("alt+tab")

def exeFocus(tokens, mode):
    # https://stackoverflow.com/questions/44735798/pywin32-how-to-get-window-handle-from-process-handle-and-vice-versa

    log.debug("app to focus: '{}'".format(tokens[0]))
    if len(tokens) != 1:
        gui.showError("Incorrect\nusage of focus")
        log.warn("focus used without exactly one token")
        return ([], mode)


    process_name = None
    if tokens[0] == 'WORD':
        process_name = 'WINWORD.EXE'
    else:
        process_name = tokens[0].lower() + '.exe'

    handles = window_properties.getMainWindowHandles(process_name, expect_one=True)
    if not handles:
        gui.showError("No app to focus")
        return ([], mode)

    # NOTE: we choose an arbitrary handle if there's more than one
    handle = handles[0]

    try:
        win32gui.SetForegroundWindow(handle)
    except Exception:
        try:
            # SetForegroundWindow is unreliable
            # workarounds: https://stackoverflow.com/questions/3772233/
            win32gui.ShowWindow(handle, win32con.SW_MINIMIZE)
            win32gui.ShowWindow(handle, win32con.SW_SHOWNORMAL)
            win32gui.SetForegroundWindow(handle)
        except Exception:
            log.error("couldn't focus app '{}'".format(tokens[0]))
            gui.showError("Couldn't focus app")
            return ([], mode)

    # Display the window normally (i.e. not minimized/maximized)
    win32gui.ShowWindow(handle, win32con.SW_SHOWNORMAL)

def exeMaximize(tokens, mode):

    if tokens:
        gui.showError("Incorrect\nusage of maximize")

    handle = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(handle, win32con.SW_MAXIMIZE)


def exeMinimize(tokens, mode):
    if tokens:
        gui.showError("Incorrect\nusage of minimize")

    handle = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(handle, win32con.SW_MINIMIZE)

def exeCancel(tokens, mode):
    """Remove all follow pop-ups and leave follow mode"""

    # NOTE: this could be extended to exit insert mode, etc.
    pyautogui.hotkey('escape')
    self.mode &= ~self.FOLLOW

def exeCopy(tokens, mode):
    keyboard.press_and_release("ctrl+c")

def exePaste(tokens, mode):
    keyboard.press_and_release("ctrl+v")

def exeRecord(tokens, mode):
    """TODO:
        Add ability to record macros.
        Tokens could be "Start" or "End" with the macro commands
        Sandwiched between "Record start" and "record end"
    """
    pass

def exeKeystroke(tokens, mode):
    if len(tokens) == 1:
        try:
            keyboard.press_and_release(tokens[0])
        except ValueError:
            log.error("bad keystroke '{}'".format(tokens[0]))
            gui.showError('Invalid usage')
    else:
        log.Logger.log(log.ParseError.TYPE, tokens)

def exeSearch(tokens):
    """Searchs text in the address bar
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

def forwardBrowser(tokens, mode):
    tokenStr = ' '.join(tokens)
    if tokenStr in browserKeywords:
        # Hacky interception of next few chars to send with follow
        if tokenStr == 'FOLLOW' or tokenStr == 'OPEN':
            mode = GlobalMode.FOLLOW
        send_message(encode_message(browserKeywords[tokenStr]))

    elif tokens[0] == 'SEARCH':
        exeSearch(tokens[1:])
    elif len(tokens) > 1 and tokens[0] == "NEW" and tokens[1] == "TAB":
        keyboard.press_and_release("ctrl+t")
    else:
        log.parse_error(log.ParseError.BROWSER, tokenStr)

    return ([], mode)

wordCmds = {
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
        'EXCLAMATION': 'shift+!',
        'QUESTION': 'shift+/',
        'SLASH': '/',
        'COLON': 'shift+:',
        'SEMICOLON': ';',
        'APOSTROPHE': '\'',
        'QUOTE': 'shift+\"',
        'OPEN PARENTHESIS': 'shift+(',
        'CLOSE PARENTHESIS': 'shift+)',
        'AMPERSAND': 'shift+&',
        'DOLLAR': 'shift+$',
        'STAR': 'shift+*',
        'LEFT ALIGN': 'ctrl+l',
        'CENTER ALIGN': 'ctrl+e',
        'RIGHT ALIGN': 'ctrl+r',
        'UNDO': 'ctrl+z',
        'RE DO': 'ctrl+y',
        'INDENT': 'tab',
        'REMOVE INDENT': 'shift+tab',
        'NEW LINE': 'enter',
        'NEWLINE': 'enter',
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

class WordForwarder:
    def __init__(self):
        self.mode = WordMode.NAVIGATE

    def forward(self, tokens, globalMode):
        log.debug("In word, current mode: " + self.mode.name)
        log.debug("Received tokens: " + ' '.join(tokens))
        tokenStr = ' '.join(tokens)
        if tokenStr in WordMode.__members__:
            self.mode = WordMode[tokenStr]
            return ([], globalMode)

        # FIXME: I think insert mode can be handled in one central location, which
        #        is in the Parser at the moment. Feel free to add a word-specific 
        #        INSERT mode back if it's infeasible/dumb to do. 
        #        
        #        *** In fact, if the parser's mode is NORMAL then it may 
        #        intercept words that are being said even if word's mode is INSERT
        #if self.wordMode == "INSERT":
        #    keyboard.write(tokenStr.lower())
        #    return ([], globalMode)

        if tokenStr in wordCmds[self.mode.name]:
            keyboard.press_and_release(wordCmds[self.mode.name][tokenStr])
            return ([], globalMode)

        #This is because we support "down X" where x is arbitrary
        elif tokens[0] in ["UP", "DOWN", "LEFT", "RIGHT"]:
            try:
                num = w2n.word_to_num(tokens[1:])
            except Exception as e:
                #raise Exception("Navigate (U/D/L/R) did not receive a number arg")
                return
            for i in range(num):
                keyboard.press_and_release(wordCmds[self.mode.name][tokens[0]])
                time.sleep(.1)

