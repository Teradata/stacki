# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgError, ParamValue


class Command(stack.commands.list.command,
		stack.commands.OSArgumentProcessor,
		stack.commands.ApplianceArgumentProcessor,
		stack.commands.HostArgumentProcessor):

	"""
	List the storage partition configuration for one of the following:
	global, os, appliance or host.

	<arg optional='1' type='string' name='host'>
	This argument can be nothing, a valid 'os' (e.g., 'redhat'), a valid
	appliance (e.g., 'backend') or a host.
	If nothing is supplied, then the global storage partition
	configuration will be output.
	</arg>

	<param type="bool" name="globalOnly" optional="0" default="n">
	Flag that specifies if only the 'global' partition entries should
	be displayed.
	</param>

	<example cmd='list storage partition backend-0-0'>
	List host-specific storage partition configuration for backend-0-0.
	</example>

	<example cmd='list storage partition backend'>
	List appliance-specific storage partition configuration for all
	backend appliances.
	</example>

	<example cmd='list storage partition'>
	List all storage partition configurations in the database.
	</example>

	<example cmd='list storage partition globalOnly=y'>
	Lists only global storage partition configuration i.e. configuration
	not associated with a specific host or appliance type.
	</example>
	"""

	def run(self, params, args):
		scope = None
		oses = []
		appliances = []
		hosts = []

		globalOnly, = self.fillParams([('globalOnly', 'n')])
		globalOnlyFlag = self.str2bool(globalOnly)

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
			if globalOnlyFlag:
				query = """select scope, device, mountpoint, size, fstype, options, partid 
					from storage_partition
					where scope = 'global'
					order by device,partid,fstype, size"""
			else:
				query = """(select scope, device, mountpoint, size, fstype, options, partid
					from storage_partition where scope = 'global') UNION ALL
					(select a.name, p.device, p.mountpoint, p.size,
					p.fstype, p.options, p.partid from storage_partition as p inner join
					nodes as a on p.tableid=a.id where p.scope='host') UNION ALL
					(select a.name, p.device, p.mountpoint, p.size,
					p.fstype, p.options, p.partid from storage_partition as p inner join
					appliances as a on p.tableid=a.id where
					p.scope='appliance') order by scope,device,partid,size,fstype"""
		elif scope == 'os':
			#
			# not currently supported
			#
			return
		elif scope == 'appliance':
			query = """select scope, device, mountpoint, size, fstype, options, partid
				from storage_partition where scope = "appliance"
				and tableid = (select id from appliances
				where name = '%s') order by device,partid,fstype, size""" % args[0]
		elif scope == 'host':
			query = """select scope, device, mountpoint, size, fstype, options, partid
				from storage_partition where scope="host" and
				tableid = (select id from nodes
				where name = '%s') order by device,partid,fstype, size""" % args[0]

		if not query:
			return

		self.beginOutput()

		self.db.execute(query)

		i = 0
		for row in self.db.fetchall():
			name, device, mountpoint, size, fstype, options, partid = row
			if size == -1:
				size = "recommended"
			elif size == -2:
				size = "hibernation"

			if name == "host" or name == "appliance":
				name = args[0]	

			if mountpoint == 'None':
				mountpoint = None

			if fstype == 'None':
				fstype = None

			if partid == 0:
				partid = None

			self.addOutput(name, [device, partid, mountpoint,
				size, fstype, options])

			i += 1

		self.endOutput(header=['scope', 'device', 'partid', 'mountpoint', 'size', 'fstype', 'options'], trimOwner=False)
