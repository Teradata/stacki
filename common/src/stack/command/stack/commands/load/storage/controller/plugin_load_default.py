# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@

import stack.commands
from stack.exception import ArgNotFound


class Plugin(stack.commands.ApplianceArgumentProcessor,
             stack.commands.OSArgumentProcessor,
             stack.commands.HostArgumentProcessor,
             stack.commands.EnvironmentArgumentProcessor,
             stack.commands.Plugin):

	def provides(self):
		return 'default'

	def removal(self, host,):
		"""Removes previous entries and return determined scope."""
		# first remove all existing entries
		scope = 'global'
		if host == 'global':
			self.owner.call('remove.storage.controller', ['scope=global', 'adapter=*', 'enclosure=*', 'slot=*'])
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
			self.owner.call('remove.' + scope + '.storage.controller', [host, 'adapter=*', 'enclosure=*', 'slot=*'])
		return scope


	def run(self, args):
		hosts = args

		for host in hosts.keys():
			scope = self.removal(host)

			arrayids = []
			extra = []
			for a in hosts[host].keys():
				if type(a) == int:
					arrayids.append(a)
				else:
					extra.append(a)
			arrayids.sort()
			arrayids.extend(extra)

			for array in arrayids:
				cmdargs = []
				if host != 'global':
					cmdargs.append(host)
				cmdargs += [ 'arrayid=%s' % array ]

				if 'raid' in hosts[host][array].keys():
					raidlevel = hosts[host][array]['raid']
					cmdargs.append('raidlevel=%s' % raidlevel)

				if 'slot' in hosts[host][array].keys():
					slots = []
					for slot in hosts[host][array]['slot']:
						if type(slot) == type(0):
							slots.append( '%d' % slot)
						else:
							slots.append(slot)

					cmdargs.append('slot=%s' % ','.join(slots))

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
						hotspares.append('%d' % hotspare)

					cmdargs.append('hotspare=%s' % ','.join(hotspares))

				if self.owner.force:
					cmdargs.append('force=y')

				if scope != 'global':
					self.owner.call('add.' + scope + '.storage.controller', cmdargs)
				else:
					self.owner.call('add.storage.controller', cmdargs)

