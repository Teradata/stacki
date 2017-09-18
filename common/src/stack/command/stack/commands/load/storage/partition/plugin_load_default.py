# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.ApplianceArgumentProcessor,
	stack.commands.HostArgumentProcessor, stack.commands.Plugin):

	"""
	Plugin that invokes 'stack add storage partition' and adds
	the partitions to the database.
	"""
	def provides(self):
		return 'default'


	def run(self, args):
		hosts = args
		for host in hosts.keys():
			#
			# first remove the entries for this host
			#
			if host == 'global':
				target = []
			else:
				target = [ host ]
			self.owner.call('remove.storage.partition', target)

			# Get list of devices for this host
			devices = hosts[host].keys()
			devices.sort()

			# Loop through all devices in the list
			for device in devices:
				partition_list = hosts[host][device]

				# Add storage partitions for this device
				for partition in partition_list:
					cmdargs = []
					if host != 'global':
						cmdargs.append(host)
					cmdargs += [ 'device=%s' % device ]

					mountpt = partition['mountpoint']
					size = partition['size']
					type = partition['type']
					options = partition['options']
					partid = partition['partid']

					if mountpt:
						cmdargs.append('mountpoint=%s' % mountpt)
					if type:
						cmdargs.append('type=%s' % type)

					cmdargs.append('size=%s' % size)
					if options:
						cmdargs.append('options=%s' % options)
					if partid:
						cmdargs.append('partid=%s' % partid)

					self.owner.call('add.storage.partition',
						cmdargs)
