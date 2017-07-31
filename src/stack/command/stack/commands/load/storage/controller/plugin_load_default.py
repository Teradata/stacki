# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@

import stack.commands

class Plugin(stack.commands.ApplianceArgumentProcessor,
	stack.commands.HostArgumentProcessor, stack.commands.Plugin):

	def provides(self):
		return 'default'


	def run(self, args):
		hosts = args

		for host in hosts.keys():
			#
			# first remove all existing entries
			#
			cmdargs = []

			if host != 'global':
				cmdargs.append(host)
			cmdargs += [ 'adapter=*', 'enclosure=*', 'slot=*' ]

			self.owner.call('remove.storage.controller', cmdargs)

			arrayids = hosts[host].keys()
			arrayids.sort()

			for array in arrayids:
				cmdargs = []
				if host != 'global':
					cmdargs.append(host)
				cmdargs += [ 'arrayid=%s' % array ]

				if 'raid' in hosts[host][array].keys():
					raidlevel = hosts[host][array]['raid']
					cmdargs.append('raidlevel=%s'
						% raidlevel)

				if 'slot' in hosts[host][array].keys():
					slots = []
					for slot in hosts[host][array]['slot']:
						if type(slot) == type(0):
							slots.append(
								'%d' % slot)
						else:
							slots.append(slot)

					cmdargs.append('slot=%s'
						% ','.join(slots))

				if 'enclosure' in hosts[host][array].keys():
					enclosure = hosts[host][array]['enclosure'].strip()
					cmdargs.append('enclosure=%s' % enclosure)

				if 'adapter' in hosts[host][array].keys():
					adapter = hosts[host][array]['adapter'].strip()
					cmdargs.append('adapter=%s' % adapter)

				if 'options' in hosts[host][array].keys():
					options = hosts[host][array]['options']
					cmdargs.append('options="%s"' % options)

				if 'hotspare' in hosts[host][array].keys():
					hotspares = []
					for hotspare in hosts[host][array]['hotspare']:
						hotspares.append('%d'
							% hotspare)

					cmdargs.append('hotspare=%s'
						% ','.join(hotspares))

				if self.owner.force:
					cmdargs.append('force=y')
			
				self.owner.call('add.storage.controller',
					cmdargs)

