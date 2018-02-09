import json
import os

curPath = os.getcwd()

#Change path in manifest.json
with open("manifest.json", "r") as f:
    s = f.read()

js = json.loads(s)
js['path'] = curPath + "\\forwarder.bat"

with open("manifest.json", "w") as f:
    json.dump(js, f)


#Change path in forwarder.bat
with open("forwarder.bat", "r") as f:
    lines = f.readlines()

lines[2] = "call python " + curPath + "\\forwarder.py"

with open("forwarder.bat", "w") as w:
    w.writelines(lines)


#Change path in forwarder.reg
with open("forwarder.reg", "r", encoding="utf-16") as infile:
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

fw = open("forwarder.reg", "w", encoding="utf-16")
fw.writelines(lines)
fw.close()