# SpeechV

SpeechV serves as an interface between the user and existing computer applications. Specifically, SpeechV enables users to do research online and compose documents using only their voice. It is designed to work with Mozilla Firefox and Microsoft Word in a Windows environment.

## Installation

1. Install Firefox, Python3 and npm

2. Open Administrator command prompt (SpeechV must be run on windows 10 with administrator privileges)

3. Goto SpeechV directory

4. Run `python config.py`

5. Restart command prompt

6. Goto SpeechV/extension directory

7. Run `npm install`

8. Run `npm install -g web-ext`

9. Run `npm start`

## How to start SpeechV

1. Open a command prompt to load the extension

2. Goto SpeechV/extension directory

3. Run `web-ext run`. This starts a special firefox, which will start up SpeechV

## Getting familiar with SpeechV

### The tutorial and command list can be found [here](tzaranek.github.io "SpeechV Documentation") or by saying "help" while using SpeechV.



# Developer Information

## Running release version

Following launch steps entitled "How to start SpeechV" in README.md launches the application as intended for the end-user. It will launch a GUI that displays the state of the application. The possible states are:

    NAVIGATE - "Normal" command mode. The majority of commands are issued through here
    INSERT - Sends raw text to the top application. Used for voice to text typing.
    FOLLOW - Awaiting letters to follow a button in Firefox or Word.
    SETTINGS - Displays the settings menu and permits abbreviated settings commands.
    SLEEPING - Ignores any spoken commands until woken by a wake word.
    HELP - Displays the help menu.

Firefox will also launch, and due to issues that we encountered with Firefox native messaging, this is the only instance of firefox that we can control using SpeechV (but new tabs are okay!)

## Using the debugger

Debugging SpeechV using voice commands is time consuming and cumbersome, and so running SpeechV by running debug.py will open up a debugging shell in addition to the GUI and Firefox. By using the debugger, you have the ability to type commands instead of speaking them. The debugger works as follows:

- The debugger issues one alt-tab to focus on another window
    - In order to ensure subsequent commands are directed at a specific application (e.g. Word) use "Focus word" first.
- The debugger issues the typed command to the switched to application.
- The debugger focuses back on the command prompt to await the next command.

The debugger also has the ability to run "test cases" which are files consisting of series of commands in the batch_input folder. To run a test case, use "debug batch `<file>`" When running a test, the debugger will not do any alt-tabbing or focusing back to the command prompt between individual commands in the test case.

While the debugger is running, a temporary DEBUG_FLAG file will be created in the root folder. While a batch input is running, a temporary BATCH_FLAG will be created in the root folder.

## Settings

Settings are stored as JSON in config.cfg in the root SpeechV folder. A default configuration will be generated if the file does not exist. Currently, we have fields for stored macros, voice timeout, and SpeechV GUI window size.

## Logging

Normal print statement output will likely be lost. All error logging and debugging output is and should be displayed using the included log module, which prints to log.txt in the root of the SpeechV folder. Log.txt is overwritten on each launch of SpeechV, so be careful to save any important output. The convention we have been using is as follows:

    log.error - Used to display stack traces and caught exceptions
    log.warn - Used to display when potentially unsafe conditions are present
    log.info - Used to display informative text about the current state
    log.debug - Used to display miscellaneous output in the spirit of print statement debugging
    log.blank - Used to display a blank line

Use these functions as you would print.
