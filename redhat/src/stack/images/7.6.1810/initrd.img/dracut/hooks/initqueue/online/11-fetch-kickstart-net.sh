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

# Find locations to the kickstart files.
locations=""

case $kickstart in
    nfs*)
        # Construct URL for nfs:auto.
        if [ "$kickstart" = "nfs:auto" ]; then
            # Construct kickstart URL from dhcp info.
            # Server is next_server, or the dhcp server itself if missing.
            . /tmp/net.$netif.dhcpopts
            server="${new_next_server:-$new_dhcp_server_identifier}"
            # Filename is dhcp 'filename' option, or '/kickstart/' if missing.
            filename="/kickstart/"
            # Read the dhcp lease file and see if we can find 'filename'.
            { while read line; do
                val="${line#filename }"
                if [ "$val" != "$line" ]; then
                    eval "filename=$val" # Drop quoting and semicolon.
                fi
              done
            } < /tmp/net.$netif.lease
            kickstart="nfs:$server:$filename"
        fi

        # URLs that end in '/' get '$IP_ADDR-kickstart' appended.
        if [[ $kickstart == nfs*/ ]]; then
            kickstart="${kickstart}${new_ip_address}-kickstart"
        fi

        # Use the prepared url.
        locations="$kickstart"
    ;;
    http*|ftp*)
        # Use the location from the variable.
        locations="$kickstart"

        # Or use the locations from the file.
        # We will try them one by one until we succeed.
        [ -f /tmp/ks_urls ] && locations="$(</tmp/ks_urls)"
    ;;
    *)
        warn "unknown network kickstart URL: $kickstart"
        return 1
    ;;
esac

# If we're doing sendmac, we need to run after anaconda-ks-sendheaders.sh
if getargbool 0 inst.ks.sendmac kssendmac; then
    newjob=$hookdir/initqueue/settled/fetch-ks-${netif}.sh
else
    newjob=$hookdir/initqueue/fetch-ks-${netif}.sh
fi

# We need extra quotation marks to safely iterate over locations in a job.
quoted_locations="$(for l in $locations; do printf '"%s" ' "$l" ; done)"

# STACKI
#
# don't execute this next section of code
#

if [ 0 -eq 1 ]
then

# Create a new job.
cat > $newjob <<__EOT__
. /lib/url-lib.sh
. /lib/anaconda-lib.sh
info "anaconda: kickstart locations are $locations"

for kickstart in $quoted_locations; do
    info "anaconda: fetching kickstart from \$kickstart"

    if fetch_url "\$kickstart" /tmp/ks.cfg; then
        info "anaconda: successfully fetched kickstart from \$kickstart"
        parse_kickstart /tmp/ks.cfg
        run_kickstart
        break
    else
        warn "anaconda: failed to fetch kickstart from \$kickstart"
    fi
done
rm \$job # remove self from initqueue
__EOT__

fi

#
# STACKI
#
# instead, execute this section of code to get the kickstart file
#
udevadm settle --timeout=60

info "anaconda: STACKI get kickstart file"

# Setup ld.conf for /opt/stack/lib (python3 needs this)
if [ ! -f /etc/ld.so.conf ]; then
	echo "include ld.so.conf.d/*.conf" > /etc/ld.so.conf
fi

echo /opt/stack/lib > /etc/ld.so.conf.d/stacki.conf

ldconfig

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
			mkdir -p /tmp/stack_site
			cat /tmp/ks.xml | /opt/stack/bin/stack list host profile chapter=main   2>  /tmp/kgen.debug > /tmp/ks.cfg
			cat /tmp/ks.xml | /opt/stack/bin/stack list host profile chapter=stacki 2>> /tmp/profile_stack_site.debug > /tmp/stack_site/__init__.py
			parse_kickstart /tmp/ks.cfg
			run_kickstart
			fini=1
		else
			warn "failed to fetch kickstart from $kickstart"
			sleep 2
		fi
	done
fi

