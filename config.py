import json
import os
import sys
import subprocess

curPath = os.getcwd()

#Generate manifest.json
manifest_template = {
    "name": "speechV.py",
    "description": "Forwards SpeechV commands as keystrokes",
    "path": "C:\\Users\\Lawrence Wu\\Documents\\SpeechV\\speechV.bat",
    "type": "stdio",
    "allowed_extensions": [
        "vim-vixen@i-beam.org"
    ]
}                                                                                                                                                                  
manifest_template['path'] = curPath + "\\speechV.bat"

with open("manifest.json", "w") as f:
    json.dump(manifest_template, f)


#Generate speechV.bat
with open("speechV.bat", "w") as w:
    lines = [
        "@echo off",
        "",
        "call python \"" + curPath + "\\speechV.py\""
        ]
    w.write("\n".join(lines))


#Generate speechV.reg
with open("speechV.reg", "w", encoding="utf-16") as w:
    lines = [
        "Windows Registry Editor Version 5.00",
        "",
        "[HKEY_LOCAL_MACHINE\\SOFTWARE\\Mozilla\\NativeMessagingHosts\\speechV.py]",
        "@=\"" + curPath + "\\manifest.json" + "\""
        ]
    w.write("\n".join(lines))


# Run registery install
subprocess.check_call(["C:\\Windows\\System32\\reg.exe", "IMPORT", "speechV.reg"])


# install python dependencies
try: 
    python_path = sys.executable
    pip_path = os.path.join(os.path.dirname(python_path), "Scripts\\pip.exe")
    print("Where pip should be: {}".format(pip_path))
    subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
except:
    print("Could not find pip. Please install pip and then run `pip install -r requirements.txt`.")



# set google application credentials
with open("credentials.bat", "w") as w:
    credential_path = "\"" + curPath + "\\credentials.json" + "\""
    w.write("setx GOOGLE_APPLICATION_CREDENTIALS {}".format(credential_path))

subprocess.check_call(["credentials.bat"], shell=True)

