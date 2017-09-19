#!/opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import subprocess
import sys
import os
import httplib
import random
import time
import json
import string

sys.path.append('/tmp')
from stack_site import *

sys.path.append('/opt/stack/lib')
from stacki_storage import *

#
# functions
#

def sendit(server, req, partinfo):
	status = 0

	h = httplib.HTTPSConnection(server, key_file = None, cert_file = None)
	h.putrequest('GET', '/install/sbin/public/setDbPartitions.cgi')

	h.putheader('X-Stack-PartitionInfo', json.dumps(partinfo))

	try:
		h.endheaders()
		response = h.getresponse()
		status = response.status
	except:
		#
		# assume the error occurred due to an
		# authorization problem
		#
		status = 403
		pass

	h.close()
	return status

##
## MAIN
##

nukedisks = []
disks = getHostDisks(nukedisks)

devices = []
for disk in disks:
	for part in disk['part']:
		device = '/dev/%s' % part
		if device not in devices:
			devices.append(device)

	for raid in disk['raid']:
		device = '/dev/%s' % raid
		if device not in devices:
			devices.append(device)

	for lvm in disk['lvm']:
		device = '/dev/mapper/%s' % lvm
		if device not in devices:
			devices.append(device)

host_fstab = getHostFstab(devices)
partitions = getHostPartitions(disks, host_fstab)

partinfo = {}
for p in partitions:
	if p['device'] not in partinfo.keys():
		partinfo[p['device']] = []

	part = (p['diskpart'], None, p['size'], None,
		p['fstype'], None, None, p['mountpoint'], p['uuid'])

	partinfo[p['device']].append(part)

random.seed(int(time.time()))

if 'Kickstart_PrivateKickstartHost' in attributes:
	host = attributes['Kickstart_PrivateKickstartHost']

	retries = 0
	while retries < 3:
		status = sendit(host, 
			'/install/sbin/public/setDbPartitions.cgi',
			partinfo)
	
		if status == 200:
			break
		else:
			time.sleep(random.randint(0, 30))
			retries += 1

