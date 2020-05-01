#!/opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import os
import sys
import json
import syslog
import stack.api

def setPartitionInfo(host, part):
	cmd = [ host ]

	(dev,sect,size,id,fstype,fflags,pflags,mnt,uuid) = part

	if dev:
		cmd.append('device=%s' % dev)
	if sect:
		cmd.append('sectorstart=%s' % sect)
	if size:
		cmd.append('size=%s' % size)
	if id:
		cmd.append('partid=%s' % id)
	if fstype:
		cmd.append('fs=%s' % fstype)
	if fflags:
		cmd.append('formatflags=%s' % fflags)
	if pflags:
		cmd.append('partitionflags=%s' % pflags)
	if mnt:
		cmd.append('mountpoint=%s' % mnt)
	if uuid:
		cmd.append('uuid=%s' % uuid)

	stack.api.Call('add host partition', cmd)

	return

##
## MAIN
##
ipaddr = None
if 'REMOTE_ADDR' in os.environ:
	ipaddr = os.environ['REMOTE_ADDR']
if not ipaddr:
	sys.exit(0)

syslog.openlog('setDbPartitions.cgi', syslog.LOG_PID, syslog.LOG_LOCAL0)

syslog.syslog(syslog.LOG_INFO, 'remote addr %s' % ipaddr)

if 'HTTP_X_STACK_PARTITIONINFO' in os.environ:
	partinfo = os.environ['HTTP_X_STACK_PARTITIONINFO']
	try:
		partinfo = json.loads(partinfo)
	except:
		syslog.syslog(syslog.LOG_ERR, 'invalid partinfo %s' % partinfo)
		partinfo = None

	if partinfo:
		stack.api.Call('remove host partition', [ ipaddr ])

		for disk in partinfo.keys():
			for part in partinfo[disk]:
				setPartitionInfo(ipaddr, part)

# The following attributes are one shot booleans and
# should always be reset even if the partinfo was corrupt.

stack.api.Call('set host attr', [ ipaddr, 'attr=nukedisks', 'value=false'])
stack.api.Call('set host attr', [ ipaddr, 'attr=nukecontroller', 'value=false'])
stack.api.Call('set host attr', [ ipaddr, 'attr=secureerase', 'value=false'])

print('Content-type: application/octet-stream')
print('Content-length: %d' % (len('')))
print('')
print('')

syslog.closelog()

