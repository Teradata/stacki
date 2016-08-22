#!/bin/bash
# fetch-kickstart-net - fetch kickstart file from the network.
# runs from the "initqueue/online" hook whenever a net interface comes online

# initqueue/online hook passes interface name as $1
netif="$1"

# we already processed the kickstart - exit
[ -e /tmp/ks.cfg.done ] && return 0

# no kickstart requested - exit
[ -n "$kickstart" ] || return 0

# user requested a specific device, but this isn't it - exit
[ -n "$ksdevice" ] && [ "$ksdevice" != "$netif" ] && return 0

command -v getarg >/dev/null || . /lib/dracut-lib.sh
. /lib/url-lib.sh
. /lib/anaconda-lib.sh

if [ "$kickstart" = "nfs:auto" ]; then
    # construct kickstart URL from dhcp info
    # server is next_server, or the dhcp server itself if missing
    . /tmp/net.$netif.dhcpopts
    server="${new_next_server:-$new_dhcp_server_identifier}"
    # filename is dhcp 'filename' option, or '/kickstart/' if missing
    filename="/kickstart/"
    # read the dhcp lease file and see if we can find 'filename'
    { while read line; do
        val="${line#filename }"
        if [ "$val" != "$line" ]; then
            eval "filename=$val" # drop quoting and semicolon
        fi
      done
    } < /tmp/net.$netif.lease
    kickstart="nfs:$server:$filename"
fi

# kickstart is appended with '$IP_ADDR-kickstart' if ending in '/'
if [ "${kickstart%/}" != "$kickstart" ]; then
    kickstart="${kickstart}${new_ip_address}-kickstart"
fi

info "anaconda fetching kickstart from $kickstart"

# STACKI
grep -q "frontend" /proc/cmdline
if [ $? -eq 0 ]; then
	if fetch_url "$kickstart" /tmp/ks.cfg; then
		parse_kickstart /tmp/ks.cfg
		run_kickstart
	else
		warn "failed to fetch kickstart from $kickstart"
	fi
else
	numcpus=`grep -c processor /proc/cpuinfo`
	arch=`uname -p`

	#
	# keep trying to get a kickstart file
	#
	fini=0
	while [ $fini -eq 0 ]
	do
		info "STACKI: kickstart: $kickstart?os=redhat&arch=$arch&np=$numcpus"
		echo "STACKI: kickstart: $kickstart?os=redhat&arch=$arch&np=$numcpus" > /run/install/k.debug
		echo "STACKI: kickstart: $kickstart?os=redhat&arch=$arch&np=$numcpus" > /tmp/k.debug
		/bin/curl -w "%{http_code}\\n" -o /tmp/ks.xml --insecure \
			--local-port 1-100 --retry 3 \
			"$kickstart?os=redhat&arch=$arch&np=$numcpus" > /tmp/httpcode
		httpcode=`cat /tmp/httpcode`
		if [ "$httpcode" -eq "200" ]
		then
			cat /tmp/ks.xml | \
			/opt/stack/bin/stack list host profile native=true  2> /tmp/kgen.debug > /tmp/ks.cfg
			parse_kickstart /tmp/ks.cfg
			run_kickstart
			fini=1
		else
			warn "failed to fetch kickstart from $kickstart"
			sleep 2
		fi
	done
fi

# if fetch_url "$kickstart" /tmp/ks.cfg; then
#    parse_kickstart /tmp/ks.cfg
#    run_kickstart
# else
#    warn "failed to fetch kickstart from $kickstart"
# fi
# STACKI
