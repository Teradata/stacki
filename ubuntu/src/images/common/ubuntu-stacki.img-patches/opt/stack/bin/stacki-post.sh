#!/bin/sh
ldconfig
# start up sshd - now you don't need the network_console
/bin/mkdir -p /target/root/.ssh
/opt/stack/bin/stacki-ssh-keys.py intarget
# configure network interfaces
/opt/stack/bin/network-interfaces-config.py > /tmp/net.log 2>&1
# give ourselves the ability to hold the installation prior to the start of preseed
#

/opt/stack/bin/stacki-debug.py

while [ -f /tmp/debug ]; do 
	sleep 10
done
