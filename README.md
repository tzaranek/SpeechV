# SpeechV

SpeechV serves as an interface between the user and existing computer applications. Specifically, SpeechV enables users to do research online and compose documents using only their voice. It is designed to work with Mozilla Firefox and Microsoft Word in a Windows environment.

## Prerequisites

Install Firefox, Python3, npm, and portaudio (http://portaudio.com/docs/v19-doxydocs/tutorial_start.html)

## Installation

1. Open Administrator command prompt

2. Goto SpeechV directory

3. Run `python config.py`

4. Restart command prompt

5. Goto SpeechV/extension directory

6. Run `npm install`

7. Run `npm install -g web-ext`

8. Run `npm start`

## How to start SpeechV

1. Open a command prompt to load the extension

2. Goto SpeechV/extension directory

3. Run `web-ext run`

## How to use SpeechV

SpeechV recognizes voice commands and translates them to actions executed by your computer. SpeechV can execute a few types of actions: keyboard shortcuts, Windows actions, browser actions and Microsoft Word actions. In addition, you can create custom commands (macros) as well as aliases for existing commands to suit your needs. The microphone can also be adjusted for your individual speech patterns.

Instructions on how to use SpeechV can be accessed when you are using the application via the **help** command.

### Keyboard shortcuts

You can execute a keyboard shortcut in SpeechV by simply saying the names of the keys to be pressed. Most keyboard shortcuts require the control, shift or alt key to be held. To do this, you say **hold** followed by the key to be held, the names of the other keys, followed by **escape** to release all held keys. Multiple keys can be held at the same time.

For example, to switch between applications, say **hold alt** followed by **tab** (as many times as necessary) then **escape**. To go to the security screen, say **hold control hold alt delete escape**.

### Windows actions

Besides the functionality afforded by the keyboard shortcuts, actions such as resizing and moving windows can be executed using SpeechV.

**Resize left/right**: Move current app into the left/right half of the screen
**Resize up/down**: Move current app into top/bottom half of the screen
**Resize file**: Make current app fullscreen

### Browser actions

SpeechV supports navigating 
web pages by finding and labelling all links/input fields on the page. You can then select an input field or follow a link using the label. Commands for viewing web pages, opening tabs and other browser functions are supported.

#### Navigating web pages

**Follow**: Label links and input fields    
    - **<label>** Open link in current tab, enter text into input field, or click button.   
**Open**: Label links and input fields   
    - **<label>** Open link in new tab. Invalid entry if input field is selected.

**Back**: Go back in history   
**Forward**: Go forward in history

#### Viewing pages
**Up/down**: Scroll vertically   
**Left/right**: Scroll horizontally   
**Control up/down**: Scroll vertically by half of a screen   
**Control upper/downer**: Scroll pages by a screen   
**Top/bottom**: Scroll to top/bottom of page   
**Zero/dollar**: Scroll a page to leftmost/rightmost   
**Zoom in/out**: Zoom in/out   
**Zoom default**: Set default zoom level   

#### Browser commands
**Delete**: Close current tab   
**Undo**: Reopen closed tab   
**Previous/next**: Select previous/next tab   
**Refresh**: Reload current tab   
**Duplicate**: Duplicate current tab   
**Find**: Search for text on a page   
**Address**: Select address box   
**New tab**: Open a new tab   
**New window**: Open a new window   
**Print**: Print current page   
**Save**: Save current page   

### Microsoft Word actions
Commands for Microsoft Word are broken up into three categories: Navigate, Highlight, and Insert. To enter each mode, simply say its name, allowing access to that categories' command set until another mode is switched to.
### Navigate: Allows navigation around the document 
**Up (X)**: Moves the cursor up one line, or a number of lines if followed by an optional number argument X     
**Down (X)**: Moves the cursor down one line, or a number of lines if followed by an optional number argument X     
**Left (X)**: Moves the cursor left one word, or a number of words if followed by an optional number argument X     
**Right (X)**: Moves the cursor right one word, or a number of words if followed by an optional number argument X       
**Paragraph up**: Moves the cursor up one paragraph     
**Paragraph down**: Moves the cursor down one paragraph     
**Page up**: Moves the cursor up one page       
**Page down**: Moves the cursor down one page       
**Period**: Enters a period at the cursor's position        
    - **<label>** Replacing period with any of the following will enter the corresponding symbol: comma, exclamation, question, slash, colon, semicolon, apostrophe, quote, open parenthesis, close parenthesis, ampersand, dollar, star    
    
**Left/Right/Center align**: Align the text at your cursor      
**Undo**: Undoes the previous text entry        
**Re do**: Redoes an undone text entry      
**Indent**: Indents at the cursor position      
**Remove indent**: Removes an indent at the cursor position     


### Highlight: Allows highlighting of text while navigating
**Down (X)**: Moves the cursor and highlights down one line, or a number of lines if followed by an optional number argument X  
**Up (X)**: Moves the cursor up and highlights one line, or a number of lines if followed by an optional number argument X  
**Right (X)**: Moves the cursor right and highlights one word, or a number of words if followed by an optional number argument X    
**Left (X)**: Moves the cursor left and highlights one word, or a number of words if followed by an optional number argument X  
**Bold**: Bolds the highlighted text    
**Italics**: Italicizes the highlighted text    
**Underline**: Underlines the highlighted text  
**Delete**: Deletes the highlighted text    
**All**: Highlights the entire document     
**Increase size**: Increases the size of the highlighted text   
**Decrease size**: Decreases the size of the highlighted text   
**Caps**: Cycles the highlighted text between UPPER CASE, lower case, and Title Case    

### Insert: Allows insertion of voice commands to text within the document
Use your voice to enter in text. Ending a voice sample with "period" will end your sentence with a period and begin to format your next sentence.


### Creating macros and aliases
**Record start**: Begin recording a macro   
    - **<label>** Between these two commands, any commands issued will be recorded  
**Record end**: Finish recording a macro    
    - **<label>** After ending a recording, a prompt to name the macro and a confirmation prompt will appear to complete the process.   

### Adjusting microphone settings (coming soon)
If speech recognition is not performing well, you are likely experiencing one of two problems:   
1. SpeechV cuts you off while you're still speaking   
2. SpeechV can't hear you or processes commands when you're not speaking

These can be fixed by accessing the **settings** panel.

To address problem 1, increase the audio timeout setting. This is the amount of silence that signals the end of a command. Increasing audio timeout allows for longer pauses when speaking, but slows down overall performance. 

To address problem 2, recalibrate the microphone. SpeechV will listen to your surroundings and automatically adjust to distinguish background noise from voice input.
