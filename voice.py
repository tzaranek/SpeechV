#!/usr/bin/env python3
"""Convert voice commands to text and forward to parser."""

import speech_recognition as sr
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

from demo import Demos

import log

import state
import time
import traceback
k = 0
d = Demos()


def recalibrate():
    sr.Recognizer().adjust_for_ambient_noise(sr.Microphone())

def recognize(command_set):
    #Set up a counter and instance of demos
    global k
    global d
    cmd = None
    #Start with testThenWrite, and then progress to other demos
    if k == 0:
        cmd = d.searchFromNavbar()
    # elif k == 1:
    #     cmd = d.testThenWrite()
    # elif k == 2:
    #     cmd = d.writeMultipleSentences()
    # elif k == 3:
    #     cmd = d.openNewLink()
    # elif k == 4:
    #     cmd = d. displayHelpMenus()

    #We're in a demo
    if cmd != None:
        #The current demo is over
        if cmd == "":
            #Go to next demo and reset the internal demo counter
            k += 1
            d.resetCounter()
    return cmd
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
    global restartLoop
    AUDIO_TIMEOUT = 0.5 # length of pause marking end of command

    with open('command_set.txt', 'r') as myfile:
        str_command_set = myfile.read()

    command_set = str_command_set.split('\n')

    r = sr.Recognizer()
    s = state.state(g)
    time.sleep(5)
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source) # listen for 1 second to calibrate the energy threshold for ambient noise levels
        r.pause_threshold = AUDIO_TIMEOUT

        while True:
            #Worth it to change this to a cv later?
            # while not s.ready:
            #     time.sleep(0.25)
                
            try:
                #print("Say something!") # TODO: change to GUI alert
                g.ready()
                log.debug("Before listen")
                time.sleep(2)

                # recognize speech using Google Cloud Speech API            
                log.debug("Pre recognize")
                response = recognize(command_set)
                s.parse(response)
                log.debug(response)
                g.updateCommands(response)
            except Exception as e:
                log.error(str(e))
                log.error(traceback.format_exc())
                raise e
            
            g.setMode(s.mode)

            # TODO: check that speech consists of valid commands
            # TODO: forward speech to parser


if __name__ == "__main__":
    voiceLoop()