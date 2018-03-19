#!/usr/bin/env python3
"""Convert voice commands to text and forward to parser."""

import log


import win32file
import speech_recognition as sr
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types


import parsing
import os
import time
import traceback
import sys
import keyboard
from globs import gui, r, mic
from word2number import w2n
import settings

def adjustTimeout(tokens):
    if len(tokens) != 3 or tokens[1] != "POINT":
        raise AttributeError("Ill-formed timeout command")
    try:
        wholeNum = w2n.word_to_num(tokens[0])
        decimal = w2n.word_to_num(tokens[2])
        r.pause_threshold = wholeNum+decimal/10
        log.info("Changed audio timeout to: " + str(r.pause_threshold))
        config = settings.loadConfig()
        config["SETTINGS"]["TIMEOUT"] = r.pause_threshold
        settings.saveConfig(config)
    except:
        raise AttributeError("Number conversion failed in adjust timeout")

def recalibrate():
    #We are now adjusting it automatically instead of calling calibrate
    log.info("Recalibrate is deprecated, it now happens automatically")


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

def voiceLoop():
    global restartLoop
    
    config = settings.loadConfig()
    AUDIO_TIMEOUT = config["SETTINGS"]["TIMEOUT"] # length of pause marking end of command

    with open('command_set.txt', 'r') as myfile:
        str_command_set = myfile.read()

    command_set = str_command_set.split('\n')

    in_debug_mode = False
    if os.path.exists('DEBUG_FLAG'):
        in_debug_mode = True
        log.info("debug mode activated")
        opened = False
        while not opened:
            try:
                pipe = win32file.CreateFile(
                        r'\\.\pipe\named_pipe',
                        win32file.GENERIC_READ | win32file.GENERIC_WRITE, 
                        win32file.FILE_SHARE_WRITE | win32file.FILE_SHARE_READ,
                        None, win32file.OPEN_EXISTING, 0, None)
                opened = True
            except Exception as e:
                log.error("HELLO WORLD")
                log.error(str(e))
                log.error(traceback.format_exc())
                time.sleep(1)

        time.sleep(1) 
    else:
        log.info("voice mode activated")


    p = parsing.Parser()
    with mic as source:
        #Automatically adjust for ambient noise instead of calling calibrate
        r.dynamic_energy_threshold = True
        r.pause_threshold = AUDIO_TIMEOUT


        while True:                
            try:
                gui.ready()

                raw_command = ''
                if in_debug_mode:
                    message = win32file.ReadFile(pipe, 4096)
                    log.debug('pipe message: ', message[1].decode())
                    raw_command = message[1].decode()
                else:
                    audio = r.listen(source)

                    # recognize speech using Google Cloud Speech API            
                    log.debug("Pre recognize")
                    raw_command = recognize(audio, command_set)

                gui.processing()

                if in_debug_mode and not os.path.exists('BATCH_FLAG'):
                    keyboard.press_and_release("alt+tab")
                    time.sleep(1) # give OS time to alt-tab
                if raw_command == -1:
                    raise ValueError("Failed to recognize speech")
                p.parse(raw_command)

                if os.path.exists('BATCH_FLAG'):
                    # send an ACK to tell them we're ready for more input
                    win32file.WriteFile(pipe, 'ACK'.encode())
                elif in_debug_mode:
                    time.sleep(1) # give the user time to see the result
                    keyboard.press_and_release("alt+tab")

                gui.updateCommands(raw_command)
            except Exception as e:
                log.error(str(e))
                log.error(traceback.format_exc())
                gui.showError("Error parsing\nTry again.")
            
            gui.setMode(p.mode)

if __name__ == "__main__":
    voiceLoop()
