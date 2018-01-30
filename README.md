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
