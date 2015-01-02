#!/bin/sh
cd out/production/massive-ironman
../../../lejos/bin/nxjlink -od debuginfo -o App.nxj Main
scp App.nxj acer.dezgeg.me:/tmp/
ssh acer.dezgeg.me $(readlink -f ../../../lejos/bin/nxjupload) -r -u /tmp/App.nxj
