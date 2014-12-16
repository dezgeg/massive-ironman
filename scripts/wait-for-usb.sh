#!/bin/bash

echo "Waiting for USB device..."
while true; do
    if lsusb -d 0694:0002 >/dev/null; then
        echo "Found USB device, waiting for it to be flashable..."
        while lsusb -d 0694:0002 >/dev/null; do
            if lsusb -v -d 0694:0002 2>/dev/null | egrep -q 'iSerial.*[0-9A-F]{8}'; then
                echo "Found it."
                exit 0
            fi
            sleep 0.5
        done
        echo "USB device disconnected."
    fi
    sleep 0.5
done
