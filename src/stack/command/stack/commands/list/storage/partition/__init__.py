# @SI_Copyright@
# @SI_Copyright@
# @SI_Copyright@

import stack.commands

class Command(stack.commands.list.command,
		stack.commands.OSArgumentProcessor,
		stack.commands.ApplianceArgumentProcessor,
		stack.commands.HostArgumentProcessor):

	"""
	List the storage partition configuration for one of the following:
	global, os, appliance or host.

	<arg optional='1' type='string' name='host'>
	This argument can be nothing, a valid 'os' (e.g., 'redhat'), a valid
	appliance (e.g., 'compute') or a host.
	If nothing is supplied, then the global storage partition
	configuration will be output.
	</arg>

	<param type="bool" name="globalOnly" optional="0" default="n">
	Flag that specifies if only the 'global' partition entries should
	be displayed.
	</param>

	<example cmd='list storage partition compute-0-0'>
	List host-specific storage partition configuration for compute-0-0.
	</example>

	<example cmd='list storage partition compute'>
	List appliance-specific storage partition configuration for all
	compute appliances.
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
			self.abort('must supply zero or one argument')

		if not scope:
			if args[0] in oses:
				scope = 'os'
			elif args[0] in appliances:
				scope = 'appliance'
			elif args[0] in hosts:
				scope = 'host'

		if not scope:
			self.abort('argument "%s" must be a ' % args[0] + \
				'valid os, appliance name or host name')

		query = None
		if scope == 'global':
			if globalOnlyFlag:
				query = """select scope, device, mountpoint, size, fstype
					from storage_partition
					where scope = 'global'
					order by device, mountpoint"""
			else:
				query = """(select scope, device, mountpoint, size, fstype
					from storage_partition 
					where scope = 'global'
					order by device, mountpoint) UNION ALL
					(select a.name, p.device, p.mountpoint, p.size, 
					p.fstype from storage_partition as p inner join nodes 
					as a on p.tableid=a.id where p.scope='host' 
					order by p.size, p.fstype) UNION ALL 
					(select a.name, p.device, p.mountpoint, p.size,
					p.fstype from storage_partition as p inner join 
					appliances as a on p.tableid=a.id where 
					p.scope='appliance' order by p.size, p.fstype)"""
		elif scope == 'os':
			#
			# not currently supported
			#
			return
		elif scope == 'appliance':
			query = """select scope, device, mountpoint, size, fstype
				from storage_partition where scope = "appliance"
				and tableid = (select id from appliances
                                where name = '%s')""" % args[0]
		elif scope == 'host':
			query = """select scope, device, mountpoint, size, fstype
				from storage_partition where scope="host" and 
				tableid = (select id from nodes 
				where name = '%s')""" % args[0]

		if not query:
			return

		self.beginOutput()

		self.db.execute(query)

		i = 0
		for row in self.db.fetchall():
			name, device, mountpoint, size, fstype = row
		
			if name == "host" or name == "appliance":
				name = args[0]	
			self.addOutput(name, [ device, mountpoint, 
				size, fstype])

			i += 1
		self.endOutput(header=['scope', 'device', 'mountpoint', 'size', 
			'fstype' ], trimOwner = 0)
