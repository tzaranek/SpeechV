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

## Tutorial: recipes for common tasks

(TODO: prettify tutorials in html format)
SpeechV's philosophy is that common tasks should be doable with a small set of high impact commands. In this section, you can see these high impact commands in action. Be sure to read the notes to the right of each command-- they contain valuable information on similar commands as well as details 


(sidenote TODO: rename zero/dollar)
(sidenote TODO: rename delete to close tab or something more intuitive)

NOTE: recipes should be readable in any order. 

NOTE: recipes should be shown in a two column format such that the left column
      lists each command in the recipe, while the right details what the command on
      the left does, as well as notes on the command and possibly similar commands
      users might want to know about

NOTE: once we have an html format to work with, I'll write up these recipes in full from the outlines below

### Recipes for Web Browsing
want to demonstrate:
 * following, opening
 * scrolling
 * searching
 * go back and forward in history
 * close tab
 * switch tabs
 * find
 * bookmark usage


Recipes to write
 * [Task: Read up on a term] search for patent and do research on it
    * satisfies following, scrolling, searching, find
    * show picture of what follow pop-ups look like
 * [Task: Create and use a bookmark] search patent and bookmark it. then use bookmark
 * [Task: Compare two web pages] search for larceny and burglary and compare pages
    * satisfies 'open', tab switching, close tab, history navigation

### Recipes for Word Processing
want to demonstrate:
 * follow - how to navigate menus, esp. for saving
 * opening word and a document (must use follow)
 * dictation and switching between insert and navigate
    * show period, comma insertion. comment on symbol support
    * connected vs standalone text
 * bold as written
 * highlight a line and bold it - make reference to other highlight verbs as well
 * highlight all
 * moving cursor with left/right/down/up
 * move by paragraph


Recipes to write
 * [Task: Save and reopen a document] Open a document, save, close word, open new document
    * satisfies menu navigation, follow for menus
 * [Task: Write in a document]
    * insert title, highlight and bold it, write a sentence below which ends in period, end with '...' by repeating period
    * talk about connected vs standalone text insertion
    * satisfies dictation, highlighting
 * [Task: Edit a document] highlight all and change font, spacing, delete some text and add period at bottom
    * satisfies following, cursor movement with higlight, moving by paragraph

### Recipes for Managing Applications
want to demonstrate
 * focus
 * alt-tab
 * resize
 * terminate
 * minimize
 * launch

Recipes to write
 * [Task: Working side-by-side] launch word, focus firefox, alt-tab between
    * satisfies resize, focus, alt-tab, limitation of launch
 * [Task: Hide applications] launch word, minimize, focus, terminate
    * talk about why terminate sucks

### Recipes for Customization
want to demonstrate
 * recording and using macros
 * where to start for modifying settings

Recipes to write:
 * [Task: Record a macro for side-by-side work] Put firefox on write, word on left
 * [Task: Enlarge user interface] use resize command in settings

### Navigating the web

1. Execute a Google search    
`Search puppies`

2. Open the images tab  
`Follow` to populate the screen with labels corresponding to links and input fields. Give the corresponding label for the images tab.

3. Scrolling    
`Down` for more puppies!

4. Working with multiple tabs    
`New tab` to search for kittens!    
`Previous tab` to go back to the puppies.

### Editing word documents

1. Inserting text    
```
Insert
Puppies
New paragraph
Puppies are cute period
```
SpeechV replaces phrases that end with 'period' or 'comma' with the corresponding punctuation. New lines and line breaks are also supported.   
`Navigate` to end text insertion

2. Moving your cursor around    
Use `up/down/left/right` to move your cursor around the document.

3. Punctuation, indentation and formatting    
You can also insert punctuation as necessary, such as `exclamation` and `open parenthesis`.    
Adjust alignment using `center/left/right align`.

4. Formatting regions of text   
To delete, bold or format regions of text, use `highlight` to enter the highlighting mode. When in highlight, `up/down/left/right` expands the selected region of text. `Bold/italics/underline` formats the selected region as desired.

5. Advanced formatting   
SpeechV allows you to access the toolbar in Microsoft Word using the command `follow`.    
For example, to make a bulleted list:
```
Follow
H
U
Cancel
```    
Every follow must end with a cancel! This is a known limitation that we are currently working on.

## Full list of commands in SpeechV

Instructions on how to use SpeechV can be accessed when you are using the application via the **help** command.

### Windows actions

Besides the functionality afforded by the keyboard shortcuts, actions such as resizing and moving windows can be executed using SpeechV.

**Resize left/right**: Move current app into the left/right half of the screen      
**Resize up/down**: Move current app into top/bottom half of the screen    
**Resize full**: Make current app fullscreen    
**Move**: Moves the SpeechV GUI to the opposite corner  
**Launch `<application>`**: Attempts to launch the given application. A limited number of applications are supported because of limited Windows support. "Firefox" and "Word" are officially supported.     
**Focus `<application>`**: Focuses on the given open application    
**Terminate**: Closes the current application without saving or confirming  
**Copy**: Copy the highlighted data     
**Paste**: Paste the data in the clipboard      


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
**Search <query>**: Executes a google search for the given query   
**Find**: Search for text on a page   
**Address**: Select address box   
**New tab**: Open a new tab   
**New window**: Open a new window   
**Print**: Print current page   
**Save**: Save current page   


### Microsoft Word actions
Commands for Microsoft Word are broken up into three categories: Navigate, Highlight, and Insert. To enter each mode, simply say its name, allowing access to that categories' command set until another mode is switched to.
### Navigate: Allows navigation around the document 
**Up <number>**: Moves the cursor up one line, or a number of lines if followed by an optional number argument  
**Down <number>**: Moves the cursor down one line, or a number of lines if followed by an optional number argument  
**Left <number>**: Moves the cursor left one word, or a number of words if followed by an optional number argument  
**Right <number>**: Moves the cursor right one word, or a number of words if followed by an optional number argument     
**Paragraph up**: Moves the cursor up one paragraph     
**Paragraph down**: Moves the cursor down one paragraph     
**Page up**: Moves the cursor up one page       
**Page down**: Moves the cursor down one page       
**Period**: Enters a period at the cursor's position        
    - **<label>** Replacing period with any of the following will enter the corresponding symbol: comma, exclamation, question, slash, colon, semicolon, apostrophe, quote, open parenthesis, close parenthesis, ampersand, dollar, star   
**Follow**: Label buttons to navigate the word GUI      
    
**Left/Right/Center align**: Align the text at your cursor      
**Undo**: Undoes the previous text entry        
**Re do**: Redoes an undone text entry      
**Indent**: Indents at the cursor position      
**Remove indent**: Removes an indent at the cursor position          
**New line**: Makes a new line at the cursor position 


### Highlight: Allows highlighting of text while navigating
**Down <number>**: Moves the cursor and highlights down one line, or a number of lines if followed by an optional number argument   
**Up <number>**: Moves the cursor up and highlights one line, or a number of lines if followed by an optional number argument   
**Right <number>**: Moves the cursor right and highlights one word, or a number of words if followed by an optional number argument     
**Left <number>**: Moves the cursor left and highlights one word, or a number of words if followed by an optional number argument  
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

### Adjusting microphone settings
If speech recognition is not performing well, you are likely experiencing one of two problems:   
1. SpeechV cuts you off while you're still speaking     
2. SpeechV processes cannot recognize your voice or processes audio when you're not speaking

Problem one can be fixed by accessing the **settings** panel. From there, increase the voice timeout setting. This is the amount of silence that signals the end of a command. Increasing audio timeout allows for longer pauses when speaking, but slows down overall performance. 

Problem two is likely an issue with your environment. SpeechV tries to automatically detect and adjust for ambient noise, but consider using SpeechV in a quiet environment for optimal performance.

