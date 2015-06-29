# @SI_Copyright@
# @SI_Copyright@

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

					cmdargs.append('mountpoint=%s' % mountpt)
					cmdargs.append('size=%s' % size)
					cmdargs.append('type=%s' % type)

					self.owner.call('add.storage.partition',
						cmdargs)

