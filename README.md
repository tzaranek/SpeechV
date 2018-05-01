# SpeechV


SpeechV is a speech-only computer interface that enables quick, intuitive computer usage, specifically targeting research workflows. Web browsing, word processing, and application management (e.g. switching between firefox and word) are the three key features, all of which work towards supporting research workflows. 

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

4. Say "help" to open a tutorial page. You can also visit speechv/extension/help_menus/help.html instead

# Developer Information

A more technical explanation is appropriate for developers. However, if you're a user, you should instead look at the tutorial (say "help" on SpeechV startup)

## Design Approach

Like Vim, SpeechV provides enhanced navigation by interpreting input through the lens of the "current mode." This mode-based approach pervades all aspects of SpeechV's design. For example, some commands like "follow" are shown to the user in the guise of a multi-part command, yet the implementation leverages an internal mode, which is abstracted away from the user (in this case "follow mode"). To understand SpeechV, you must understand the modes:

* *NAVIGATE* - Input is handled according to the first "word" in the chunk of speech being processed. This first "word", called the *command*, is then compared with a dictionary of known commands. Externally visible
* *INSERT* - Input is sent directly to the top application, unless it is a command to switch modes. Externally visible
* *FOLLOW* - Input is expected to be an argument for the "follow" command. Internally visible
* *SETTINGS* - Displays the settings menu and permits abbreviated settings commands. Externally visible
* *STANDBY* - Ignores any spoken commands until woken by a wake word. Externally Visible
* *SETTINGS* - Input is used to navigate the settings menus


## Using the debugger

For developers, the voice interface is inherently cumbersome. The debugging interface cuts out speech processing and replaces it with a textual, terminal-based interface that significantly streamlines development, both in terms of time and ease.

However, there is one quirk to the debugging interface: SpeechV commands operate on the foremost application, but when using the debugging interface, the command line must be on top. To work around this limitation, the following steps are executed on each command:
1. The debugger issues one alt-tab, placing the most second most recently used application on top
2. The command is executed in full
3. The debugger issues a "focus" onto the command prompt, placing control back on the debugging interface

The debugger also has the ability to run "test cases" which are files consisting of series of commands in the batch_input folder. To run a test case, use "debug batch `<file>`" When running a test, the debugger will not do any alt-tabbing or focusing back to the command prompt between individual commands in the test case.

## Settings

Settings are stored as JSON in config.cfg in the root SpeechV folder. A default configuration will be generated if the file does not exist. Currently, we have fields for stored macros, voice timeout, and SpeechV GUI window size.

## Logging

Normal print statement output will likely be lost. All error logging and debugging output is and should be displayed using the included log module, which prints to log.txt in the root of the SpeechV folder. Log.txt is overwritten on each launch of SpeechV, so be careful to save any important output. The convention we have been using is as follows:

* `log.error` - Used to display stack traces and caught exceptions
* `log.warn` - Used to display when potentially unsafe conditions are present
* `log.info` - Used to display informative text about the current state
* `log.debug` - Used to display miscellaneous output in the spirit of print statement debugging
* `log.blank` - Used to display a blank line

Use these functions as you would print

## Weird Behaviors

In order to connect the firefox extension with the python implementation, we've set the project up such that starting up the Firfox extension will start up the python code. Unfortunately, this strongly couples firefox with the rest of SpeechV. One side effect of this is that if Firefox is closed, all of SpeechV will shut down. The one benefit, however, is expediency in implementation. Future work on this project should refactor the connection between web browsing and general computer navigation.