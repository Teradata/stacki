# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@

import stack.commands
from stack.exception import *

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
				query = """select scope, device, mountpoint, size, fstype, options 
					from storage_partition
					where scope = 'global'
					order by fstype, size"""
			else:
				query = """(select scope, device, mountpoint, size, fstype, options 
					from storage_partition 
					where scope = 'global'
					order by fstype, size) UNION ALL
					(select a.name, p.device, p.mountpoint, p.size, 
					p.fstype, p.options from storage_partition as p inner join 
					nodes as a on p.tableid=a.id where p.scope='host' 
					order by p.fstype, p.size) UNION ALL 
					(select a.name, p.device, p.mountpoint, p.size,
					p.fstype, p.options from storage_partition as p inner join 
					appliances as a on p.tableid=a.id where 
					p.scope='appliance' order by p.fstype, p.size)"""
		elif scope == 'os':
			#
			# not currently supported
			#
			return
		elif scope == 'appliance':
			query = """select scope, device, mountpoint, size, fstype,
				options from storage_partition where scope = "appliance"
				and tableid = (select id from appliances
                                where name = '%s') order by fstype, size""" % args[0]
		elif scope == 'host':
			query = """select scope, device, mountpoint, size, fstype,
				options from storage_partition where scope="host" and 
				tableid = (select id from nodes 
				where name = '%s') order by fstype, size""" % args[0]

		if not query:
			return

		self.beginOutput()

		self.db.execute(query)

		i = 0
		for row in self.db.fetchall():
			name, device, mountpoint, size, fstype, options = row
			if size == -1:
				size = "recommended"
			elif size == -2:
				size = "hibernation"	
			if name == "host" or name == "appliance":
				name = args[0]	
			self.addOutput(name, [ device, mountpoint, 
				size, fstype, options])

			i += 1
		self.endOutput(header=['scope', 'device', 'mountpoint', 'size', 
			'fstype', 'options'], trimOwner = 0)
