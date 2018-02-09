from enum import Enum
import time
import re
import win32gui, win32con, win32api, win32process

def getVisibleWindows():
    def enumHandler(hwnd, results):
        if not win32gui.IsWindowVisible(hwnd):
            return
        results.append(hwnd)
    handles = []
    win32gui.EnumWindows(enumHandler, handles)
    return handles
            

def currentApp():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())

def getFileProperties(fname):
    """
    Read all properties of the given file return them as a dictionary.
    """
    propNames = ('Comments', 'InternalName', 'ProductName',
        'CompanyName', 'LegalCopyright', 'ProductVersion',
        'FileDescription', 'LegalTrademarks', 'PrivateBuild',
        'FileVersion', 'OriginalFilename', 'SpecialBuild')

    props = {'FixedFileInfo': None, 'StringFileInfo': None, 'FileVersion': None}

    try:
        # backslash as parm returns dictionary of numeric info corresponding to VS_FIXEDFILEINFO struc
        fixedInfo = win32api.GetFileVersionInfo(fname, '\\')
        props['FixedFileInfo'] = fixedInfo
        props['FileVersion'] = "%d.%d.%d.%d" % (fixedInfo['FileVersionMS'] / 65536,
                fixedInfo['FileVersionMS'] % 65536, fixedInfo['FileVersionLS'] / 65536,
                fixedInfo['FileVersionLS'] % 65536)

        # \VarFileInfo\Translation returns list of available (language, codepage)
        # pairs that can be used to retreive string info. We are using only the first pair.
        lang, codepage = win32api.GetFileVersionInfo(fname, '\\VarFileInfo\\Translation')[0]

        # any other must be of the form \StringfileInfo\%04X%04X\parm_name, middle
        # two are language/codepage pair returned from above

        strInfo = {}
        for propName in propNames:
            strInfoPath = u'\\StringFileInfo\\%04X%04X\\%s' % (lang, codepage, propName)
            ## print str_info
            strInfo[propName] = win32api.GetFileVersionInfo(fname, strInfoPath)

        props['StringFileInfo'] = strInfo
    except:
        pass

    return props


def getApplicationName(hwnd):
    (_threadId, processId) = win32process.GetWindowThreadProcessId(hwnd)
    pHandle = win32api.OpenProcess(
                win32con.PROCESS_QUERY_INFORMATION |
                win32con.PROCESS_VM_READ, 0, processId)
    pExeName = win32process.GetModuleFileNameEx(pHandle, 0)
    props = getFileProperties(pExeName)
    return props['StringFileInfo']['FileDescription']


class state:
    def __init__(self):
        # Define bits for modes we can be in
        self.NORMAL     = 2**0
        self.ALT        = 2**1
        self.CTRL       = 2**2
        self.INSERT     = 2**3
        self.CLEAR      = 0

        self.mode = self.NORMAL
        self.commands = {
                "control": {
                    "tab": self.changeTab
                },
                "caps": {
                    "lock": self.switchMode
                },
                "alt": {
                    "tab": self.changeApps
                }
        }

    def switchMode(self, _):
        self.mode = self.INSERT if self.mode & self.NORMAL else self.NORMAL

    def changeApps(self, appName):
        print(getApplicationName(win32gui.GetForegroundWindow()))
        windows = getVisibleWindows()
        for hwnd in windows:
            if ' '.join(appName) == getApplicationName(hwnd):
                print(hwnd)
                win32gui.BringWindowToTop(hwnd)
                win32gui.SetForegroundWindow(hwnd)

    def changeTab(self, _):
        browsers = ["Google Chrome", "Firefox"]
        if currentApp()[0] in browsers:
            print("Forwarding...")
        else:
            print("awef")

    def curMode(self):
        return self.mode

    def recursiveParse(self, words, levelDict):
        w, rest = words[0], words[1:]
        if w in levelDict:
            if isinstance(levelDict[w], dict):
                self.recursiveParse(rest, levelDict[w])
            else:
                levelDict[w](rest)
        else:
            print("Command not found")


    def parse(self, command):
        if self.mode & self.NORMAL:
            text = re.findall(r"[a-zA-Z]+", command)
            print(text)
            self.recursiveParse(text, self.commands)
        else:
            if command == "caps lock":
                self.switchMode(command)
            else:
                print("Sending: \"{}\" to top application".format(command))

v = state()
# time.sleep(2)
v.parse("alt tab")
v.parse("alt-tab")
v.parse("control tab")
v.parse("caps lock")
v.parse("control-tab")
v.parse("alt-tab")
v.parse("caps lock")
v.parse("alt-tab Google Chrome")
