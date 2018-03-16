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
import commands
from window_properties import currentApp
from forwarder import encode_message, send_message
from mode import *
from globs import gui

class MacroManager:
    def __init__(self, config):
        self.mode = RecordMode.IDLE
        self.macroName = None
        self.macroCommands = []
        self.config = config

    def interceptCommand(self, command):
        """Returns true if the Parser has nothing left to do with the command"""
        #Handle recording commands here so we can return immediately after
        if self.mode == RecordMode.IDLE: #Not recording
            if command == "RECORD START":
                gui.startRecording()
                self.macroCommands = []
                self.mode = RecordMode.RECORDING
                return True
        elif self.mode == RecordMode.RECORDING:
            if command == "RECORD END":
                gui.endRecording()
                self.mode = RecordMode.NAMING
                return True
        elif self.mode == RecordMode.NAMING:
            self.macroName = command
            gui.macroNameEntered(command)
            self.mode = RecordMode.CONFIRMING
            return True
        elif self.mode == RecordMode.CONFIRMING:
            if command.strip().upper() == "YES":
                self.config['macros'][self.macroName] = self.macroCommands
                saveConfig(self.config)
                gui.macroNameConfirmed()
                self.mode = RecordMode.IDLE
                return True
            elif command.strip().upper() == "NO":
                gui.endRecording()
                self.mode = RecordMode.NAMING
                return True
            else:
                raise ValueError("Please answer\nyes or no")

        return False

    
    def conditionalCommit(self, command):
        """Commits the command to this macro, if we're recording"""
        if self.mode == RecordMode.RECORDING:
            self.macroCommands.append(command)



class Parser:
    def __init__(self):
        # handle input based on mode
        self.mode = GlobalMode.NAVIGATE

        # Load the configuration file into a dictionary
        try:
            self.config = loadConfig()
        except FileNotFoundError:
            # FIXME: handle case where there is no config file
            log.error("No config file found! Ignoring error for now...")
            self.config = {} 
            self.config['macros'] = {}

        self.wordForwarder = commands.WordForwarder()
        self.macroManager = MacroManager(self.config)

        # all of these functions must return one of the following:
        #  - None (this is returned if there is no explicit 'return')
        #  - A tuple of the form (A, B) where A is a list of tokens that 
        #    need to be parsed after command execution and B is the global mode
        self.commands = {
            "ALT":      commands.exeAlt,
            "RESIZE":   commands.exeResize,
            "HELP":     commands.exeHelp,
            "SETTINGS": commands.exeSettings,
            "LAUNCH":   commands.exeLaunch,
            "SWITCH":   commands.exeSwitch,
            "MOVE":     gui.enter,
            "RECORD":   commands.exeRecord,
            "TYPE":     commands.exeKeystroke,
            "FOCUS":    commands.exeFocus,
            "MINIMIZE": commands.exeMinimize,
            "MAXIMIZE": commands.exeMaximize,
            "CANCEL":   commands.exeCancel,
            "CLOSE":    commands.exeClose
        }

    def parse(self, command):
        self.ready = False
        log.debug("parsing command: '{}'".format(command))
        command = command.strip().upper()

        isFullyHandled = self.macroManager.interceptCommand(command)
        if isFullyHandled:
            return

        if len(command) == 1:
            command = command.lower()

        if self.mode == GlobalMode.NAVIGATE or self.mode == GlobalMode.FOLLOW:
            command = re.sub('[!@#$\']', '', command)
            text = re.findall(r"[a-zA-Z]+", command)
            log.info("Tokens parsed: {}".format(text))

            self.parseImpl(text)
        elif self.mode == GlobalMode.INSERT:
            if command == 'NAVIGATE':
                self.mode = GlobalMode.NAVIGATE
            elif command == 'ENTER':
                # Might want to consider having this implicitly exit insert mode?
                keyboard.press_and_release('enter')
            else:
                log.info("Sending: \"{}\" to top application".format(command))
                keyboard.write(command)
                #keys = [commands.KeyboardMessage(ch) for ch in command]
                #send_message(encode_message(keys))

        else:
            # Oh no! We have a bad mode. Hopefully going back to NAVIGATE saves us
            log.error('unknown mode:', self.mode)
            self.mode = GlobalMode.NAVIGATE


        # the command was succesfull commit it if we need to
        self.macroManager.conditionalCommit(command)
        
        # sleep after parsing to allow commands to send appropriately
        time.sleep(0.5)

    def parseImpl(self, tokens, levelDict = None):
        if not tokens:
            return

        # TODO: better method of accepting letters to follow
        #   currently just takes all tokens as individual letters and sends
        #   them on assuming that there's no point in issuing commands
        #   before the link is followed. Also, there should not be more than 3
        if self.mode == GlobalMode.FOLLOW:
            # handle switch specially so that alt-tabbing works with the prompt
            if tokens[0] == 'SWITCH' and len(tokens) == 1:
                self.parseSwitch(tokens[1:])
                return
            elif tokens[0] == 'CANCEL' and len(tokens) == 1:
                commands.exeCancel([], self.mode)
                return

            self.mode = GlobalMode.NAVIGATE

            if len(tokens) > 3:
                log.warn("cannot handle more than 3 follow characters")
                return
            for token in tokens:
                if len(token) != 1:
                    log.warn("cannot handle follow token size greater than 1")
                    return

            enumerated_keys = [commands.KeyboardMessage(tok) for tok in tokens]
            send_message(encode_message(enumerated_keys))

            return

        # FIXME: we currently don't use this feature. Maybe we want to remove
        #        it so that the code is easier to read?
        if levelDict is None:
            levelDict = self.commands


        # See the comment by self.commands in __init__ for the details
        def handleCmdRet(ret):
            if ret is not None:
                leftoverTokens, self.mode = ret[0], ret[1]
                self.parseImpl(leftoverTokens, self.mode)
            
        w, rest = tokens[0], tokens[1:]
        if w in levelDict:
            if isinstance(levelDict[w], dict):
                self.parseImpl(rest, levelDict[w])
            else:
                ret = levelDict[w](rest, self.mode)
                handleCmdRet(ret)
        else:
            log.info('forwarding to current app: ', currentApp())
            if currentApp() == 'Firefox':
                ret = commands.forwardBrowser(tokens, self.mode)
                handleCmdRet(ret)
            elif currentApp() == 'Microsoft Word':
                ret = self.wordForwarder.forward(tokens, self.mode)
                handleCmdRet(ret)
            elif ' '.join(tokens) in self.config['macros']:
                self.exeMacro((self.config['macros'][' '.join(tokens)]))
            else:
                gui.showError("Unrecognized\nCommand")
                log.warn("Command not found")


    def exeMacro(commands):
        for cmd in commands:
            self.parse(cmd)
            time.sleep(1.0)

def loadConfig():
    with open("config.cfg", "r") as f:
        s = f.read()
        config = json.loads(s)
    return config 

def saveConfig(config):
    with open("config.cfg", "w") as f:
        s = json.dumps(config)
        f.write(s)
