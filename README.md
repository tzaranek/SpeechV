# SpeechV
## Set up
### Install dependencies (for Unix systems)
1. Use Homebrew to install portaudio and swig (required for dependencies)
```bash
brew install portaudio
brew install swig
```
2. Activate virtual environment
```bash
python3 -m venv env
source env/bin/activate
```
3. Install package
```bash
pip install -e .
```
4. Run!
```bash
voice
```
(Note: currently using Google Cloud Speech API to decode audio. Please don't send _too_ many requests.)

### Switching to Sphinx for decoding audio

To test Sphinx voice recognition, replace lines 18 to 24 in `voice/__main__.py` with:

```python
# recognize speech using Sphinx
try:
    print("Sphinx thinks you said " + r.recognize_sphinx(audio))
except sr.UnknownValueError:
    print("Sphinx could not understand audio")
except sr.RequestError as e:
    print("Sphinx error; {0}".format(e))
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
