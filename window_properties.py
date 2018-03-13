import win32api, win32con, win32process, win32gui, win32con
import psutil

import log

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


def currentApp():
    return getApplicationName(win32gui.GetForegroundWindow())

# https://stackoverflow.com/questions/44735798/pywin32-how-to-get-window-handle-from-process-handle-and-vice-versa
def getMainWindowHandles(process_name, expect_one=False):
    """Return a list of handles for visible windows with a given process name"""

    # find all processes with process_name
    pids = []
    for process in psutil.process_iter():
        if process.name() == process_name:
            pids.append(process.pid)

    # find all window handles with process_name
    whandles = []
    def windowFilter(handle, extra):
        if win32process.GetWindowThreadProcessId(handle)[1] in pids:
            whandles.append(handle)
        return True
    win32gui.EnumWindows(windowFilter, None)

    # find all visible/primary windows with process_name
    main_handles = []
    for handle in whandles:
        if not win32gui.IsWindowVisible(handle):
            continue
        
        parent_handle = win32gui.GetParent(handle)
        if parent_handle == 0:
            main_handles.append(handle)
            continue

        extended_style = win32api.GetWindowLong(handle, win32con.GWL_EXSTYLE)
        if extended_style & win32con.WS_EX_APPWINDOW:
            main_handles.append(handle)
            continue
    if expect_one:
        if not main_handles:
            log.warn("Expected exactly one main window for app '{}'. Found 0".format(process_name))
        elif len(main_handles) > 1:
            log.warn("Expected exactly one main window for app '{}'. Found {}"
                    .format(process_name, len(main_handles)))
            for count, handle in enumerate(main_handles):
                log.blank()
                log.debug('window ({})'.format(count))
                log.debug('window handle:', str(handle))
                log.debug('window text:', win32gui.GetWindowText(handle))
                log.debug('window placement:', win32gui.GetWindowPlacement(handle))
                log.debug('window visibility:', win32gui.IsWindowVisible(handle))

    return main_handles

