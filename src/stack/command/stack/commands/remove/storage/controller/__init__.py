# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
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
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#
# @Copyright@

import stack.commands

class Command(stack.commands.remove.command,
		stack.commands.OSArgumentProcessor,
		stack.commands.HostArgumentProcessor,
		stack.commands.ApplianceArgumentProcessor):
	"""
	Remove a storage controller configuration from the database.

        <arg type='string' name='scope'>
	Zero or one argument. The argument is the scope: a valid os (e.g.,
	'redhat'), a valid appliance (e.g., 'compute') or a valid host
	(e.g., 'compute-0-0). No argument means the scope is 'global'.
        </arg>

	<param type='int' name='adapter' optional='1'>
	Adapter address. If adapter is '*', enclosure/slot address applies to
	all adapters.
	</param>

        <param type='int' name='enclosure' optional='1'>
	Enclosure address. If enclosure is '*', adapter/slot address applies
	to all enclosures.
        </param>

        <param type='int' name='slot'>
	Slot address(es). This can be a comma-separated list. If slot is '*',
	adapter/enclosure address applies to all slots.
        </param>

	<example cmd='remove storage controller compute-0-0 slot=1'>
	Remove the disk array configuration for slot 1 on compute-0-0.
	</example>

	<example cmd='remove storage controller compute slot=1,2,3,4'>
	Remove the disk array configuration for slots 1-4 for the compute
	appliance.
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
				appliances = self.getApplianceNames(args)
			except:
				appliances = []

			try:
				hosts = self.getHostnames(args)
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

		if scope == 'global':
			name = None
		else:
			name = args[0]

                adapter, enclosure, slot = self.fillParams([ ('adapter', None), 
				('enclosure', None), ('slot', None) ])

		if not slot:
			self.abort('slot not specified')

		if adapter and adapter != '*':
			try:
				adapter = int(adapter)
			except:
				self.abort('adapter is not an integer')

			if adapter < 0:
				self.abort('adapter "%s" is not zero or a positive integer' % adapter)
		else:
			adapter = -1

		if enclosure and enclosure != '*':
			try:
				enclosure = int(enclosure)
			except:
				self.abort('enclosure is not an integer')

			if adapter < 0:
				self.abort('enclosure "%s" is not zero or a positive integer' % enclosure)
		else:
			enclosure = -1

		slots = []
		if slot and slot != '*':
			for s in slot.split(','):
				try:
					s = int(s)
				except:	
					self.abort('slot "%s" is not an integer' % s)
				if s < 1:
					self.abort('slot "%s" is not a positive integer' % s)
				if s in slots:
					self.abort('slot "%s" is listed twice' % s)

				slots.append(s)

		#
		# look up the id in the appropriate 'scope' table
		#
		tableid = None
		if scope == 'global':
			tableid = -1
		elif scope == 'appliance':
			self.db.execute("""select id from appliances where
				name = '%s' """ % name)
			tableid, = self.db.fetchone()
		elif scope == 'host':
			self.db.execute("""select id from nodes where
				name = '%s' """ % name)
			tableid, = self.db.fetchone()

		deletesql = """delete from storage_controller where
			scope = '%s' and tableid = %s """ % (scope, tableid)

		if adapter != '*':
			deletesql += ' and adapter = %s' % adapter

		if enclosure != '*':
			deletesql += ' and enclosure = %s' % enclosure

		if slot != '*':
			for slot in slots:
				dsql = '%s and slot = %s' % (deletesql, slot)
				self.db.execute(dsql)
		else:
			self.db.execute(deletesql)

