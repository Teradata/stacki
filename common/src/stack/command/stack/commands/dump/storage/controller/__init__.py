#
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#

import stack.commands


class Command(stack.commands.ApplianceArgumentProcessor,
	stack.commands.HostArgumentProcessor,
	stack.commands.dump.command):

	"""
	Dump the disk array controller configuration
	"""

	def dumpit(self, hosts):
		for scope in hosts.keys():
			for arrayid in hosts[scope].keys():
				cmd = []

				if scope != 'global':
					cmd.append(scope)

				enclosure = hosts[scope][arrayid]['enclosure']
				adapter = hosts[scope][arrayid]['adapter']
				slot = hosts[scope][arrayid]['slot']

				raidlevel = None
				if 'raidlevel' in hosts[scope][arrayid].keys():
					raidlevel = hosts[scope][arrayid]['raidlevel']

				hotspare = None
				if 'hotspare' in hosts[scope][arrayid].keys():
					hotspare = hosts[scope][arrayid]['hotspare']

				if enclosure is not None:
					cmd.append('enclosure=%s' % enclosure)
				if adapter is not None:
					cmd.append('adapter=%s' % adapter)
				if slot is not None and slot != []:
					cmd.append('slot=%s' % ','.join(slot))
				if raidlevel is not None:
					cmd.append('raidlevel=%s' % raidlevel)
				if hotspare is not None:
					cmd.append('hotspare=%s' %
						','.join(hotspare))

				cmd.append('arrayid=%s' % arrayid)

				self.dump('add storage controller %s' %
					' '.join(cmd))

	def parseit(self, scope, output):
		hosts = {}
		hosts[scope] = {}

		for o in output:
			if o['adapter'] is not None:
				adapter = '%s' % o['adapter']
			else:
				adapter = None

			if o['enclosure'] is not None:
				enclosure = '%s' % o['enclosure']
			else:
				enclosure = None

			if o['slot'] is not None:
				slot = '%s' % o['slot']
			else:
				slot = None

			if o['raidlevel'] is not None:
				raidlevel = '%s' % o['raidlevel']
			else:
				raidlevel = None

			if o['arrayid'] is not None:
				arrayid = '%s' % o['arrayid']
			else:
				arrayid = None

			if arrayid not in hosts[scope].keys():
				hosts[scope][arrayid] = {}
				hosts[scope][arrayid]['slot'] = []

			if raidlevel == 'hotspare':
				if 'hotspare' not in hosts[scope][arrayid].keys():
				
					hosts[scope][arrayid]['hotspare'] = []
				
				hosts[scope][arrayid]['hotspare'].append(slot)
				raidlevel = None
			else:
				hosts[scope][arrayid]['raidlevel'] = raidlevel
				hosts[scope][arrayid]['slot'].append(slot)

			hosts[scope][arrayid]['adapter'] = adapter
			hosts[scope][arrayid]['enclosure'] = enclosure

		return hosts
	

	def run(self, params, args):
		#
		# global configuration
		#
		output = self.call('list.storage.controller')
		hosts = self.parseit('global', output)
		self.dumpit(hosts)

		#
		# per appliance
		#
		for appliance in self.getApplianceNames():
			output = self.call('list.storage.controller',
				[ appliance ])
			if output:
				hosts = self.parseit(appliance, output)
				self.dumpit(hosts)

		#
		# per host
		#
		for host in self.getHostnames():
			output = self.call('list.storage.controller',
				[ host ])
			if output:
				hosts = self.parseit(host, output)
				self.dumpit(hosts)

