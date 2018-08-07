#!/opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import sys
import http.client
import random
import time
import json
import ssl

sys.path.append('/tmp')
try:
	from stack_site import attributes
except:
	attributes={}

sys.path.append('/opt/stack/lib')
from stacki_storage import getHostDisks, getHostFstab, getHostPartitions

#
# functions
#

context = ssl.SSLContext()
context.verify_mode = ssl.CERT_NONE


def sendit(server, partinfo):
	"""Send the discovered partition back to the stacki frontend."""
	status = 0

	h = http.client.HTTPSConnection(server, context=context)
	h.putrequest('GET', '/install/sbin/public/setDbPartitions.cgi')

	h.putheader('X-Stack-PartitionInfo', json.dumps(partinfo))

	try:
		h.endheaders()
		response = h.getresponse()
		status = response.status
	except:
		sys.stderr.write('%s\n' % response)
		sys.stderr.write('%s\n' % status)

	h.close()
	return status

def prepare_partition_info(partinfo, part):
	if part['device'] not in partinfo.keys():
		partinfo[part['device']] = []

	part_list = (part['diskpart'], part['start'], part['size'], None, part['fstype'], None, None, part['mountpoint'],
	             part['uuid'])

	partinfo[part['device']].append(part_list)
	return partinfo

#
# MAIN
#

nukedisks = []
disks = getHostDisks(nukedisks)

devices = []
partinfo = {}
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
	if disk['part'] == [] and disk['raid'] == [] and disk['lvm'] == []:
			partinfo = prepare_partition_info(partinfo, disk)


host_fstab = getHostFstab(devices)
partitions = getHostPartitions(disks, host_fstab)

for part in partitions:
	partinfo = prepare_partition_info(partinfo, part)

random.seed(int(time.time()))

if 'Kickstart_PrivateKickstartHost' in attributes:
	host = attributes['Kickstart_PrivateKickstartHost']
else:
	# Attempt to send it to myself, in case I am actually the frontend.
	host = 'localhost'

retries = 0
while retries < 3:
	status = sendit(host, partinfo)

	if status == 200:
		break
	else:
		time.sleep(random.randint(0, 30))
		retries += 1
