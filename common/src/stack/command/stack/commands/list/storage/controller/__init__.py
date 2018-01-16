#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
from stack.exception import ArgError, ParamValue


class Command(stack.commands.list.command,
		stack.commands.OSArgumentProcessor,
		stack.commands.ApplianceArgumentProcessor,
		stack.commands.HostArgumentProcessor):

	"""
	List the storage controller configuration for one of the following:
	global, os, appliance or host.

	<arg optional='1' type='string' name='host'>
	This argument can be nothing, a valid 'os' (e.g., 'redhat'), a valid
	appliance (e.g., 'backend') or a host.
	If nothing is supplied, then the global storage controller
	configuration will be output.
	</arg>

	<example cmd='list storage controller backend-0-0'>
	List host-specific storage controller configuration for backend-0-0.
	</example>

	<example cmd='list storage controller backend'>
	List appliance-specific storage controller configuration for all
	backend appliances.
	</example>

	<example cmd='list storage controller'>
	List global storage controller configuration for all hosts.
	</example>

	"""

	def run(self, params, args):
		scope = None
		oses = []
		appliances = []
		hosts = []

		if len(args) == 0:
			scope = 'global'
		elif len(args) == 1:
			try:
				oses = self.getOSNames(args)
			except:
				oses = []

			try:
				appliances = self.getApplianceNames()
			except:
				appliances = []

			try:
				hosts = self.getHostnames()
			except:
				hosts = []

		else:
			raise ArgError(self, 'scope', 'must be unique or missing')

		if not scope:
			if args[0] in oses:
				scope = 'os'
			elif args[0] in appliances:
				scope = 'appliance'
			elif args[0] in hosts:
				scope = 'host'

		if not scope:
			raise ParamValue(self, 'scope', 'valid os, appliance name or host name')

		query = None
		if scope == 'global':
			query = """select adapter, enclosure, slot, raidlevel,
				arrayid, options from storage_controller 
				where scope = 'global'
				order by enclosure, adapter, slot"""
		elif scope == 'os':
			#
			# not currently supported
			#
			return
		elif scope == 'appliance':
			query = """select adapter, enclosure, slot,
				raidlevel, arrayid, options
				from storage_controller where
				scope = "appliance" and tableid = (select
				id from appliances
				where name = '%s')
				order by enclosure, adapter, slot""" % args[0]
		elif scope == 'host':
			query = """select adapter, enclosure, slot,
				raidlevel, arrayid, options
				from storage_controller where
				scope = "host" and tableid = (select
				id from nodes where name = '%s')
				order by enclosure, adapter, slot""" % args[0]

		if not query:
			return

		name = None
		if scope == 'global':
			name = 'global'
		elif scope in [ 'appliance', 'host']:
			name = args[0]

		self.beginOutput()

		self.db.execute(query)

		i = 0
		for row in self.db.fetchall():
			adapter, enclosure, slot, raidlevel, arrayid, options = row

			if i > 0:
				name = None
			if adapter == -1:
				adapter = None
			if enclosure == -1:
				enclosure = None
			if slot == -1:
				slot = '*'
			if raidlevel == '-1':
				raidlevel = 'hotspare'
			if arrayid == -1:
				arrayid = 'global'
			elif arrayid == -2:
				arrayid = '*'
			# Remove leading and trailing double quotes
			options = options.strip("\"")

			self.addOutput(name, [ enclosure, adapter, slot,
				raidlevel, arrayid, options ])

			i += 1

		self.endOutput(header=['scope', 'enclosure', 'adapter', 'slot', 
			'raidlevel', 'arrayid', 'options' ], trimOwner=False)

