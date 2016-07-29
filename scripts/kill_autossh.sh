#!/bin/bash

for i in `ps aux | grep 'autossh' | grep -v 'grep' | awk '{ print $2 }'`; do

	echo "[!] Killing autossh connection with PID: $i";

	kill $i

done
