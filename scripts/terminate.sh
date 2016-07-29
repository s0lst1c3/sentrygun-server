#!/bin/bash
port="$1"
rhost="$2"
#echo $port
#echo $rhost
for i in `lsof -i :4444 | grep sshd | awk '{ print $2 }' `; do kill $i; done
