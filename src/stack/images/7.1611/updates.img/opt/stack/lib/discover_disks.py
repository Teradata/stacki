#!/usr/bin/python

import blivet
import os
import time

b = blivet.Blivet()

def getBlockDevices():

	disks = []
	raids = []
	done = False
	while not done:
		b.reset()
		for device in b.devices:
			if device.isDisk and not device.removable:
				if device.name not in disks:
					disks.append(device.name)
			elif device.type == 'mdarray':
				if device.name not in raids:
					raids.append('md%s' % device.name)
		if len(disks) or len(raids):
			break
		time.sleep(10)
		os.system('/bin/udevadm settle')

	return (disks, raids)

disks, raids = getBlockDevices()
file = open('/tmp/discovered.disks', 'w')
file.write('disks: %s\n' % ' '.join(disks))
file.write('raids: %s\n' % ' '.join(raids))
file.close()
