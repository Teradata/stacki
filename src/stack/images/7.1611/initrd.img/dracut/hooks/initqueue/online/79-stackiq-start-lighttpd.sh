#!/bin/bash

command -v getarg >/dev/null || . /lib/dracut-lib.sh
. /lib/url-lib.sh
. /lib/anaconda-lib.sh

info "STACKIQ: starting lighttpd"

# [ ! -h /opt ] && ln -s /updates/opt /opt

#
# initqueue/online hook passes interface name as $1
#
netif="$1"

server=""
if [ -f /tmp/net.$netif.dhcpopts ]
then
	. /tmp/net.$netif.dhcpopts
	server="${new_next_server:-$new_dhcp_server_identifier}"
fi

#
# create stack.conf for lighttpd
#
if [ "$server" != "" ]
then
	echo "var.trackers = \""$server"\"" > /tmp/stack.conf
	echo "var.pkgservers = \""$server"\"" >> /tmp/stack.conf
else
	echo "var.trackers = \"""\"" > /tmp/stack.conf
	echo "var.pkgservers = \"""\"" >> /tmp/stack.conf
fi

#
# need to copy stack.conf since /tmp gets remounted during the root pivot
#
mkdir -p /run/install/tmp
cp /tmp/stack.conf /run/install/tmp/stack.conf

#
# if lighttpd was already running, then kill it since we may have
# reconfigured it above (that is, a new /tmp/stack.conf may have been
# written).
#
LIGHTTPDPID=`ps auwx | grep lighttpd | grep -v grep | /opt/stack/bin/awk '{print $2}'`

if [ "$LIGHTTPDPID" != "" ]
then
	kill $LIGHTTPDPID
fi

#
# start lighttpd
#
/opt/lighttpd/sbin/lighttpd -f /opt/lighttpd/conf/lighttpd.conf \
	-m /opt/lighttpd/lib/

