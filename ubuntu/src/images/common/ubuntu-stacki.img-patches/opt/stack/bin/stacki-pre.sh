#!/bin/sh
# Compile library path so /opt/stack/bin/stack works.
ldconfig
#=============================================
# do the voodoo that we do
#---------------------------------------------

/opt/stack/bin/python /opt/stack/bin/stacki-profile.py
#
# stacki-profile.py outputs the file /tmp/stacki-profile.xml which contains
# two "chapters":
#
#	1) "preseed" chapter. This is the preseed.xml file.
# 	2) "stacki" chapter. This is python code that will be imported into
#		other programs that run during the install in order to
#		configure the system.
#

cat /tmp/stacki-profile.xml \
	| /opt/stack/bin/stack list host profile chapter=preseed \
	> /tmp/profile/preseed.xml

mkdir -p /tmp/stack_site/

cat /tmp/stacki-profile.xml \
	| /opt/stack/bin/stack list host profile chapter=stacki \
	> /tmp/stack_site/__init__.py

#
# configure the hardware disk array controller first
#
#/opt/stack/bin/python /opt/stack/bin/storage-controller-client.py

#
# then configure the partitions
#
#/opt/stack/bin/python /opt/stack/bin/output-partition.py > /tmp/partition.log 2>&1

mkdir -p /root/.ssh
mkdir -p /etc/ssh
/opt/stack/bin/stacki-ssh-keys.py "/" > /tmp/pre.log 2>&1
/usr/sbin/sshd -f /etc/sshd_config.installer -h /etc/ssh/ssh_host_ecdsa_key >> /tmp/pre.log 2>&1

#/opt/stack/bin/get_etc_fstab.py >> /tmp/pre.log 2>&1
#/opt/stack/bin/get_etc_fstab.py

# give ourselves the ability to hold the installation prior to the start of preseed
#

#/opt/stack/bin/stacki-debug.py

#while [ -f /tmp/debug ]; do 
#	sleep 10
#done
