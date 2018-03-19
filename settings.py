import json

def loadConfig():
    with open("config.cfg", "r") as f:
        s = f.read()
        config = json.loads(s)
    return config 

def saveConfig(config):
    with open("config.cfg", "w") as f:
        s = json.dumps(config)
        f.write(s)