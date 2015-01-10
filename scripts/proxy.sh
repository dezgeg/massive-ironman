#!/bin/bash
rm -f /tmp/nxt
$(dirname $0)/../lejos/bin/nxjsocketproxy -u &
socat TCP-LISTEN:9001,fork,reuseaddr PIPE:/tmp/nxt
