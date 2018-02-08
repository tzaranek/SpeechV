import os

curPath = os.getcwd()
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