# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgNotFound

class Plugin(stack.commands.OSArgumentProcessor,
             stack.commands.ApplianceArgumentProcessor,
             stack.commands.HostArgumentProcessor,
             stack.commands.Plugin,
             stack.commands.EnvironmentArgumentProcessor):

	"""
	Plugin that invokes 'stack add storage partition' and adds
	the partitions to the database.
	"""
	def provides(self):
		return 'default'


	def run(self, args):
		hosts = args
		for host in hosts.keys():
			# first remove the entries for this host
			scope = 'global'
			if host == 'global':
				self.owner.call('remove.storage.partition', ['scope=global','device=*'])
			# Is there a cleaner way to put this into a for loop or something?
			# I really need to loop over these functions and break when I find something.
			else:
				try:
					self.getOSNames([host])
					scope = 'os'
				except ArgNotFound:
					pass
				if scope == 'global':
					try:
						self.getApplianceNames([host])
						scope = 'appliance'
					except ArgNotFound:
						pass
				if scope == 'global':
					try:
						self.getEnvironmentNames([host])
						scope = 'environment'
					except ArgNotFound:
						pass
				if scope == 'global':
					try:
						self.getHostnames([host])
						scope = 'host'
					except ArgNotFound:
						pass
				self.owner.call('remove.' + scope + '.storage.partition', [host, 'device=*'])

			# Get list of devices for this host
			devices = []
			for d in hosts[host].keys():
				devices.append(d)
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
					parttype = partition['type']
					options = partition['options']
					partid = partition['partid']

					if mountpt:
						cmdargs.append('mountpoint=%s' % mountpt)
					if parttype:
						cmdargs.append('type=%s' % parttype)

					cmdargs.append('size=%s' % size)
					if options:
						cmdargs.append('options=%s' % options)
					if partid:
						cmdargs.append('partid=%s' % partid)

					if scope != 'global':
						cmdargs.append('scope=global')
						self.owner.call('add.' + scope + '.storage.partition', cmdargs)
					else:
						self.owner.call('add.storage.partition', cmdargs)
