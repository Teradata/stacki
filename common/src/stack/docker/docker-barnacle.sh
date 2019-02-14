#! /bin/bash
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

LOCK=/var/lock/subsys/barnacle
STACK=/opt/stack/bin/stack

if [ -x $LOCK ]; then
	exit 0
fi

set -x

cd /tmp

$STACK report siteattr > site.attrs
echo platform:docker  >> site.attrs

$STACK list node xml server attrs=site.attrs > profile.xml
cat profile.xml | $STACK list host profile chapter=main profile=bash > profile.sh 2>&1

bash profile.sh | tee barnacle.log

$STACK add    pallet /export/stack/pallets/stacki
$STACK enable pallet %
$STACK enable pallet % box=frontend


# Move CentOS repos and add EPEL (gitflow)

cd /etc/yum.repos.d
mv save/CentOS-*.repo .
yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm


touch $LOCK

# in lieu of reboot -- start all the runlevel 3 daemons

systemctl isolate multi-user.target

echo DONE | tee -a barnacle.log



