#! /bin/bash
#
# Run this before creating an AMI from the newly installed barnacle
# host. This will clean out crap and ssh keys and setup the
# stack-aws-barnacle service to run on first boot.
#
# When this complete it will shutdown the machine, and the user
# can then create a new image (AMI) from the stopped instance.
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


rm -rf /tmp/stack*
rm /root/.ssh/authorized_keys

systemctl disable stack-aws-client-register
systemctl enable stack-aws-barnacle


# CentOS
#
# dhclient needs more cleaning

if [ -x /var/lib/dhclient ]; then
	rm -rf /var/lib/dhclient/dhclient*
	rm -f  /etc/udev/rules.d/70-persistent-net.rules

	cfg=/etc/sysconfig/network-scripts/ifcfg-eth0
	if [ -f $cfg ]; then
		fgrep -v MACADDR /etc/sysconfig/network-scripts/ifcfg-eth0 > /tmp/ifcfg-eth0
		mv /tmp/ifcfg-eth0 $cfg
	fi
fi

echo
echo "Frontend Barnacle is Ready"
echo
echo "Run /sbin/init 0 to shutdown the system"
echo
