#!/usr/bin/env python3
"""Convert voice commands to text and forward to parser."""

import speech_recognition as sr
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

import log

import state
import os
import time
import traceback
import sys
import keyboard

import win32file

def loadConfig():
    with open("config.cfg", "r") as f:
        s = f.read()
        config = json.loads(s)
    return config 

def saveConfig(config):
    with open("config.cfg", "w") as f:
        s = json.dumps(config)
        f.write(s)

def recalibrate():
    sr.Recognizer().adjust_for_ambient_noise(sr.Microphone())

def recognize(audio_data, command_set):
    client = speech.SpeechClient()

    flac_data = audio_data.get_flac_data(
        convert_rate=None if 8000 <= audio_data.sample_rate <= 48000 else max(8000, min(audio_data.sample_rate, 48000)),
        convert_width=2  # audio samples must be 16-bit
    )
    
    audio = types.RecognitionAudio(content=flac_data)
    config = types.RecognitionConfig(
        encoding = enums.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=audio_data.sample_rate,
        language_code='en-US',
        speech_contexts=[speech.types.SpeechContext(
            phrases=command_set,)]
        )

    response = client.recognize(config, audio)
    
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript.strip() + " "
    if transcript == "": return -1
    return transcript

def voiceLoop(g):
    try:
        global restartLoop
        #Load the configuration file into a dictionary
        try:
            config = loadConfig()
        except FileNotFoundError:
            # FIXME: handle case where there is no config file
            log.error("No config file found! Ignoring error for now...")
            config = {} 

        AUDIO_TIMEOUT = 0.5 # length of pause marking end of command

        with open('command_set.txt', 'r') as myfile:
            str_command_set = myfile.read()

        command_set = str_command_set.split('\n')

        in_debug_mode = False
        if os.path.exists('DEBUG_FLAG'):
            in_debug_mode = True
            log.info("debug mode activated")
            pipe = win32file.CreateFile(
                    r'\\.\pipe\named_pipe',
                    win32file.GENERIC_READ, 
                    win32file.FILE_SHARE_WRITE | win32file.FILE_SHARE_READ,
                    None, win32file.OPEN_EXISTING, 0, None)
            time.sleep(1) 
        else:
            log.info("voice mode activeated")


        r = sr.Recognizer()
        s = state.state(g)
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source) # listen for 1 second to calibrate the energy threshold for ambient noise levels
            r.pause_threshold = AUDIO_TIMEOUT

            recording = False
            macro = {}
            macroCommands = []

            while True:                
                try:
                    #print("Say something!") # TODO: change to GUI alert
                    g.ready()

                    raw_command = ''
                    if in_debug_mode:
                        log.debug("reading from pipe")
                        message = win32file.ReadFile(pipe, 4096)
                        log.debug('pipe message: ', message[1].decode())
                        raw_command = message[1].decode()
                    else:
                        log.debug("Before listen")
                        audio = r.listen(source)

                        # recognize speech using Google Cloud Speech API            
                        log.debug("Pre recognize")
                        raw_command = recognize(audio, command_set)

                    g.processing()

                    if in_debug_mode:
                        s.parse('switch')
                    s.parse(raw_command)
                    if in_debug_mode:
                        time.sleep(1) # give the user time to see the result
                        s.parse('switch')

                    g.updateCommands(raw_command)
                    

                    #if not recording:
                    #    #We've begun recording a macro
                    #    if raw_command.strip().upper() == "RECORD START":
                    #        recording = True
                    #        macroCommands = []

                    #if recording:                    
                    #    #We've finished recording a macro
                    #    #Name the macro (and confirm) to finish the process
                    #    if raw_command.strip().upper() == "RECORD END":
                    #        recording = False
                    #        confirm = False
                    #        macro['commands'] = macroCommands

                    #        #While we haven't confirmed the macro's name
                    #        while not confirm:
                    #            g.showError("Name your\nmacro")
                    #            log.debug("Recording the macro name")
                    #            audio = r.listen(source)        
                    #            macroName = recognize(audio, command_set)
                    #            g.showError("Name:" + macroName + "\n'Yes' to confirm\n'No' to retry")
                    #            audio = r.listen(source)        
                    #            answer = recognize(audio, command_set)
                    #            #Ask to confirm the macro
                    #            if answer.strip().upper == "YES":
                    #                confirm = True
                    #        
                    #        #Insert the macro into the dictionary
                    #        macro['name'] = macroName
                    #        config.macros[macroName] = macroCommands
                    #        saveConfig(config)


                except Exception as e:
                    log.error(str(e))
                    log.error(traceback.format_exc())
                    g.showError("Error parsing\nTry again.")
                
                g.setMode(s.mode)

                # TODO: check that speech consists of valid commands
                # TODO: forward speech to parser
    except Exception as e:
        log.error("voice loop:", e)
        sys.exit(1)


if __name__ == "__main__":
    voiceLoop()
