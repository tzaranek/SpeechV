#!/usr/bin/env python3
"""Convert voice commands to text and forward to parser."""

import speech_recognition as sr
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

import log

import state

k = 0

def recognize(audio_data, command_set):
    # global k
    return "FOLLOW"
    # if k == 0:
    #     k += 1
    #     return "HELP"
    # elif k == 1:
    #     k += 1
    #     return "HELP CLOSE"
    # elif k == 2:
    #     k += 1
    #     return "HELP BROWSER"
    # elif k == 3:
    #     k += 1
    #     return "HELP CLOSE"
    # else:
    #     return "Done"
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
    AUDIO_TIMEOUT = 0.5 # length of pause marking end of command

    with open('command_set.txt', 'r') as myfile:
        str_command_set = myfile.read()

    command_set = str_command_set.split('\n')

    r = sr.Recognizer()
    s = state.state(g)
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source) # listen for 1 second to calibrate the energy threshold for ambient noise levels
        r.pause_threshold = AUDIO_TIMEOUT

        while True:
            #print("Say something!") # TODO: change to GUI alert
            g.ready()
            log.debug("Before listen")
            audio = r.listen(source) # can be configured for user's speech patterns - possible added functionality?

            # recognize speech using Google Cloud Speech API            
            log.debug("Pre recognize")
            response = recognize(audio, command_set)
            s.parse(response)
            log.debug(response)

            # TODO: check that speech consists of valid commands
            # TODO: forward speech to parser


if __name__ == "__main__":
    voiceLoop()