#!/usr/bin/python

import blivet

b = blivet.Blivet()
b.reset()

disks = []
raids = []
for device in b.devices:
	if device.isDisk and not device.removable:
		disks.append(device.name)
	elif device.type == 'mdarray':
		raids.append('md%s' % device.name)

file = open('/tmp/discovered.disks', 'w')
file.write('disks: %s\n' % ' '.join(disks))
file.write('raids: %s\n' % ' '.join(raids))
file.close()
