#! /bin/bash
#
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

STACK=/opt/stack/bin/stack

# generate a new siteattrs from current network config
# generate a new profile.sh
# run the profile and barnacle into a frontend

cd /tmp
$STACK report siteattr > site.attrs
echo platform:aws     >> site.attrs

ifconfig       > /dev/console
cat site.attrs > /dev/console


$STACK list node xml server attrs=site.attrs > profile.xml
cat profile.xml | $STACK list host profile chapter=main profile=bash > profile.sh 2>&1
bash profile.sh > barnacle.log 2>&1

# re-add the pallets on the disk
# enable all the pallets

cd /export/stack/pallets
for x in *; do
	if [ -d $x ]; then
		/opt/stack/bin/stack add pallet $x
	fi
done
/opt/stack/bin/stack enable pallet %

# reboot (but don't barnacle again)

systemctl disable stack-aws-barnacle
/sbin/init 6


