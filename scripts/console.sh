#!/bin/bash
if ! [ -p /tmp/nxt ]; then
    echo "No named pipe"
    exit 1
fi
stty -icanon
cat > /tmp/nxt
