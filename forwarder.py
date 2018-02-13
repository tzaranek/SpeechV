#!/usr/bin/env python -u

import json
import subprocess
import struct
import time
import sys
import log


class EncoderOverload(json.JSONEncoder):
    """
    JSONEncoder subclass that leverages an object's `__json__()` method,
    if available, to obtain its default JSON representation. 

    """
    def default(self, obj):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return json.JSONEncoder.default(self, obj)

# source: https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Native_messaging
def encode_message(message_content):
    encoded_content = json.dumps(message_content, cls=EncoderOverload)
    encoded_length = struct.pack('@I', len(encoded_content))
    log.debug(len(encoded_content))
    return {'length': encoded_length, 'content': encoded_content}


# source: https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Native_messaging
def send_message(encoded_message):
    log.warn(encoded_message)
    sys.stdout.buffer.write(encoded_message['length'])
    sys.stdout.buffer.write(encoded_message['content'].encode())
    sys.stdout.flush()



# if __name__ == "__main__":
#     # proof of concept
#     command = [
#         {
#             'key': 'f',
#             'repeat': False,
#             'shiftKey': False,
#             'ctrlKey': False,
#             'altKey': False,
#             'metaKey': False
#         },
#         {
#             'key': 'b',
#             'repeat': False,
#             'shiftKey': False,
#             'ctrlKey': False,
#             'altKey': False,
#             'metaKey': False
#         }]
#     while True:
#         time.sleep(3)
#         send_message(encode_message(command))
