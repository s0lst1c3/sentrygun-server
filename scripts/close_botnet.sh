#!/bin/bash
rhost=$1
port=$2

MYCOMMAND=`base64 -w0 ./scripts/terminate.sh`
echo $MYCOMMAND
ssh -p "$port" "$rhost" "echo $MYCOMMAND | base64 -d | sudo bash"
