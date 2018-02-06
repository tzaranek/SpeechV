#!/bin/bash

if [ "$(whoami)" != root ]; then
    >&2 echo "error: sudo required"
    exit 1
fi

# not 100% safe because of bash shenanigans but it's better than assuming the cwd
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

mkdir -p "/Library/Application Support/Mozilla/NativeMessagingHosts/"

# filename must match <name> property exactly
cp ../manifest.json "/Library/Application Support/Mozilla/NativeMessagingHosts/forwarder.json"

