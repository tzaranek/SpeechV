#!/usr/bin/env python3
"""Parse and forward voice commands to Chrome extension."""

import speech_recognition as sr

def main():
    with open('credentials.json', 'r') as myfile:
        GOOGLE_CLOUD_SPEECH_CREDENTIALS = myfile.read()
    
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)  # listen for 1 second to calibrate the energy threshold for ambient noise levels
            print("Say something!")
            audio = r.listen(source) # can be configured for user's speech patterns - possible added functionality?
            print("Decoding audio...")

        # recognize speech using Google Cloud Speech API
        try:
            print("Google Cloud Speech thinks you said " + r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS))
        except sr.UnknownValueError:
            print("Google Cloud Speech could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Cloud Speech service; {0}".format(e))


if __name__ == "__main__":
    main()