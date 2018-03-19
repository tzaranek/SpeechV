import json

def loadConfig():
    try:
        with open("config.cfg", "r") as f:
            s = f.read()
            config = json.loads(s)
    except:
        config = {"MACROS": {}, "SETTINGS": {"TIMEOUT": 0.5, "WINDOW_SIZE": 100}}
        saveConfig(config)
    return config 

def saveConfig(config):
    with open("config.cfg", "w") as f:
        s = json.dumps(config)
        f.write(s)