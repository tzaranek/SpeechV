#!/usr/bin/env python -u

import json
import subprocess
import struct
import time
import sys


# source: https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Native_messaging
def encode_message(message_content):
    encoded_content = json.dumps(message_content)
    encoded_length = struct.pack('@I', len(encoded_content))
    return {'length': encoded_length, 'content': encoded_content}


# source: https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Native_messaging
def send_message(encoded_message):
    try:
        # python 2.7 compatible - supported because firefox insists on using v2
        sys.stdout.write(encoded_message['length'])
        sys.stdout.write(encoded_message['content'].encode())
        sys.stdout.flush()
    except TypeError:
        # python 3 compatible
        sys.stdout.buffer.write(encoded_message['length'])
        sys.stdout.buffer.write(encoded_message['content'].encode())
        sys.stdout.flush()



if __name__ == "__main__":
    # proof of concept
    command = [
        {
            'key': 'f',
            'repeat': False,
            'shiftKey': False,
            'ctrlKey': False,
            'altKey': False,
            'metaKey': False
        },
        {
            'key': 'b',
            'repeat': False,
            'shiftKey': False,
            'ctrlKey': False,
            'altKey': False,
            'metaKey': False
        }]
    while True:
        time.sleep(3)
        send_message(encode_message(command))
