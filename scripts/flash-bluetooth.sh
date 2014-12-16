#!/bin/sh
cd out/production/massive-ironman
../../../lejos/bin/nxjlink -o App.nxj Main
../../../lejos/bin/nxjupload -r -b App.nxj
