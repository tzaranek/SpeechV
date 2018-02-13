# SpeechV
## Set up voice recognition
1. Install portaudio (http://portaudio.com/docs/v19-doxydocs/tutorial_start.html)

2. Set environment variable GOOGLE_APPLICATION_CREDENTIALS. Replace [PATH] with path to credentials.json
```
set GOOGLE_APPLICATION_CREDENTIALS=[PATH]
```

##Set up vim vixen extension for Windows
1. Run setupReg.py to modify the included forwarder.reg

2. Run forwarder.reg to install the registry key

3. Run web extension
```bash
cd extension
npm run start
```

4. Open a new command prompt to load the extension
```
cd extension
web-ext run
```

(See extension/CONTRIBUTING.md for more info)

##Using the GUI
Start by creating a GUIClass() object, which will start a default GUI in command mode. Then, use the included functions to modify the GUI. The GUI should be running in the main thread. Examples in test_gui.py.
