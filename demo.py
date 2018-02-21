class Demos:
    def __init__(self):
        self.__count = -1
        self.__ttw = ["FOLLOW", "g", "ESCAPE", "The Great Escape", "ESCAPE",\
        "FOLLOW", "h", "HOLD ALT", "TAB", "HOLD ESCAPE", "ESCAPE",\
        "The Great Escape was released in 1963."]

        self.__wms = ["This is my first sentence", "Here is another sentence",\
        "Time to take a break", "SAVE"]

        self.__onl = ["FOLLOW", "g", "ESCAPE", "The Great Escape", "ESCAPE",\
        "FOLLOW", "h", "OPEN", "k"]

        self.__dhm = ["HELP", "HELP CLOSE", "HELP BROWSER", "HELP CLOSE"]

        self.__sfn = ["SEARCH Hitchhiker's Guide to the Galaxy", "FOLLOW", "P"\
        "FOLLOW", "V", ""]

    #Navigate to google first
    def searchFromNavbar(self):
        self.__count += 1
        return "" if self.__count >= len(self.__sfn) else self.__sfn[self.__count]

    #Googles "The Great Escape" and then writes a sentence in word about it.
    def testThenWrite(self):
        self.__count += 1
        return "" if self.__count >= len(self.__ttw) else self.__ttw[self.__count]

    #Writes a few sentences in word and then opens the save prompt
    def writeMultipleSentences(self):
        self.__count += 1
        return "" if self.__count >= len(self.__wms) else self.__wms[self.__count]

    #Googles "The Great Escape" and opens a link in a new tab
    def openNewLink(self):
        self.__count += 1
        return "" if self.__count >= len(self.__onl) else self.__onl[self.__count]

    #Goes through the help menus
    def displayHelpMenus(self):
        self.__count += 1
        return "" if self.__count >= len(self.__dhm) else self.__dhw[self.__count]

    #Resets the counter to 0 so we can start a new demo
    def resetCounter(self):
        self.__count = -1

    """DEMO IDEAS:
        Still need to enter keystrokes to word, don't need messages though.
        Switch between tabs in firefox
        Set up an alias such that Chun-Han has two windows open, firefox and word
            and then he can say SWITCH as an alias for alt tabbing
    """