#!/bin/sh
cd out/production/massive-ironman
../../../lejos/bin/nxjlink -o App.nxj Main
../../../lejos/bin/nxjupload -r -u App.nxj
