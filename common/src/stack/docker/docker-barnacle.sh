#! /bin/bash
#
# @copyright@
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

# add EPEL for random stuff the user/dev might want
yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

$STACK add    pallet /export/stack/pallets/stacki
$STACK enable pallet stacki

touch $LOCK

# in lieu of reboot -- start all the runlevel 3 daemons

systemctl isolate multi-user.target

echo DONE | tee -a barnacle.log



