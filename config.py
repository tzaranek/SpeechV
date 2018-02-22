import json
import os
import sys
import subprocess

curPath = os.getcwd()

#Change path in manifest.json
with open("manifest.json", "r") as f:
    s = f.read()

js = json.loads(s)
js['path'] = curPath + "\\speechV.bat"

with open("manifest.json", "w") as f:
    json.dump(js, f)


#Change path in forwarder.bat
with open("speechV.bat", "r") as f:
    lines = f.readlines()

lines[2] = "call python \"" + curPath + "\\speechV.py\""

with open("speechV.bat", "w") as w:
    w.writelines(lines)


#Change path in forwarder.reg
with open("speechV.reg", "r", encoding="utf-16") as infile:
    lines = infile.readlines()

lines[3] = '@="' + curPath + "\\manifest.json" + '"'
k = lines[3]
s = ""
for l in k:
    if l == '\\':
        s += '\\'
    s += l
lines[3] = s
lines.append('\n')

fw = open("speechV.reg", "w", encoding="utf-16")
fw.writelines(lines)
fw.close()

# Run registery install
subprocess.check_call(["C:\\Windows\\System32\\reg.exe", "IMPORT", "speechV.reg"], shell=True)

try: 
    python_path = sys.executable
    pip_path = os.path.join(os.path.dirname(python_path), "Scripts\\pip.exe")
    print("Where pip should be: {}".format(pip_path))
    subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
except:
    print("Could not find pip. Please install pip and then run `pip install -r requirements.txt`.")


