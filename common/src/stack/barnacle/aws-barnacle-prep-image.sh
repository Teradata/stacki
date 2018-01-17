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
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

rm -rf /tmp/stack*
rm /root/.ssh/authorized_keys

systemctl disable stack-aws-client-register
systemctl enable  stack-aws-barnacle

/sbin/init 0
