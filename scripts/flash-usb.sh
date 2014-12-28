#!/bin/sh
cd out/production/massive-ironman
../../../lejos/bin/nxjlink -od debuginfo -o App.nxj Main
../../../scripts/wait-for-usb.sh
../../../lejos/bin/nxjupload -r -u App.nxj
