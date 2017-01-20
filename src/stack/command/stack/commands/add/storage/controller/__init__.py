# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
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
#
# @Copyright@

import stack.commands
from stack.exception import *

class Command(stack.commands.HostArgumentProcessor,
		stack.commands.ApplianceArgumentProcessor,
		stack.commands.add.command):
	"""
	Add a storage controller configuration to the database.

        <arg type='string' name='scope'>
	Zero or one argument. The argument is the scope: a valid os (e.g.,
	'redhat'), a valid appliance (e.g., 'backend') or a valid host
	(e.g., 'backend-0-0). No argument means the scope is 'global'.
        </arg>

	<param type='int' name='adapter' optional='1'>
	Adapter address.
	</param>

        <param type='int' name='enclosure' optional='1'>
	Enclosure address.
        </param>

        <param type='int' name='slot'>
	Slot address(es). This can be a comma-separated list meaning all disks
	in the specified slots will be associated with the same array
        </param>

        <param type='int' name='raidlevel'>
	RAID level. Raid 0, 1, 5, 6 and 10 are currently supported.
        </param>

        <param type='int' name='hotspare' optional='1'>
	Slot address(es) of the hotspares associated with this array id. This
	can be a comma-separated list (like the 'slot' parameter). If the
	'arrayid' is 'global', then the specified slots are global hotspares.
        </param>

        <param type='string' name='arrayid'>
	The 'arrayid' is used to determine which disks are grouped as part
	of the same array. For example, all the disks with arrayid of '1' will
	be part of the same array. Arrayids must be integers starting at 1
	or greater. If the arrayid is 'global', then 'hotspare' must
	have at least one slot definition (this is how one specifies a global
	hotspare).
	In addition, the arrays will be created in arrayid order, that is,
	the array with arrayid equal to 1 will be created first, arrayid
        equal to 2 will be created second, etc.
        </param>

	<example cmd='add storage controller backend-0-0 slot=1 raidlevel=0 arrayid=1'>
	The disk in slot 1 on backend-0-0 should be a RAID 0 disk.
	</example>

	<example cmd='add storage controller backend-0-0 slot=2,3,4,5,6 raidlevel=6 hotspare=7,8 arrayid=2'>
	The disks in slots 2-6 on backend-0-0 should be a RAID 6 with two
	hotspares associated with the array in slots 7 and 8.
	</example>
	"""

	def checkIt(self, name, scope, tableid, adapter, enclosure, slot):
		self.db.execute("""select scope, tableid, adapter, enclosure,
			slot from storage_controller where
			scope = '%s' and tableid = %s and adapter = %s and
			enclosure = %s and slot = %s""" % (scope, tableid,
			adapter, enclosure, slot))

		row = self.db.fetchone()

		if row:
			label = [ 'scope', 'name' ]
			value = [ scope, name ]

			if adapter > -1:
				label.append('adapter')
				value.append('%s' % adapter)
			if enclosure > -1:
				label.append('enclosure')
				value.append('%s' % enclosure)

			label.append('slot')
			value.append('%s' % slot)

			raise CommandError(self, 'disk specification %s %s already exists in the database' % ('/'.join(label), '/'.join(value)))


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
			raise CommandError(self, 'must supply zero or one argument')

		if not scope:
			if args[0] in oses:
				scope = 'os'
			elif args[0] in appliances:
				scope = 'appliance'
			elif args[0] in hosts:
				scope = 'host'

		if not scope:
			raise CommandError(self, 'argument "%s" must be a valid os, appliance name or host name' % arg[0])

		if scope == 'global':
			name = 'global'
		else:
			name = args[0]

                adapter, enclosure, slot, hotspare, raidlevel, arrayid, options, force = self.fillParams([
                        ('adapter', None),
                        ('enclosure', None),
                        ('slot', None),
                        ('hotspare', None),
                        ('raidlevel', None),
			('arrayid', None, True),
			('options',''),
			('force','n')
                        ])

		if not hotspare and not slot:
                        raise ParamRequired(self, [ 'slot', 'hotspare' ])
		if arrayid != 'global' and not raidlevel:
                        raise ParamRequired(self, 'raidlevel')

		if adapter:
			try:
				adapter = int(adapter)
			except:
                                raise ParamType(self, 'adapter', 'integer')
			if adapter < 0:
                                raise ParamValue(self, 'adapter', '>= 0')
		else:
			adapter = -1

		if enclosure:
			try:
				enclosure = int(enclosure)
			except:
                                raise ParamType(self, 'enclosure', 'integer')
			if enclosure < 0:
                                raise ParamValue(self, 'enclosure', '>= 0')
		else:
			enclosure = -1

		slots = []
		if slot:
			for s in slot.split(','):
				if s == '*':
					#
					# represent '*' in the database as '-1'
					#
					s = -1
				else:
					try:
						s = int(s)
					except:
                                                raise ParamType(self, 'slot', 'integer')
					if s < 0:
                                                raise ParamValue(self, 'slot', '>= 0')
					if s in slots:
                                                raise ParamError(self, 'slot', ' "%s" is listed twice' % s)
				slots.append(s)

		hotspares = []
		if hotspare:
			for h in hotspare.split(','):
				try:
					h = int(h)
				except:	
                                        raise ParamType(self, 'hotspare', 'integer')
				if h < 0:
                                        raise ParamValue(self, 'hostspare', '>= 0')
				if h in hotspares:
                                        raise ParamError(self, 'hostspare', ' "%s" is listed twice' % h)
				hotspares.append(h)

		if arrayid in [ 'global', '*' ]:
			pass
		else:
			try:
				arrayid = int(arrayid)
			except:
                                raise ParamType(self, 'arrayid', 'integer')
			if arrayid < 1:
                                raise ParamValue(self, 'arrayid', '>= 0')

		if arrayid == 'global' and len(hotspares) == 0:
                        raise ParamError(self, 'arrayid', 'is "global" with no hotspares. Please supply at least one hotspare')

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

		#
		# make sure the specification doesn't already exist
		#
		force = self.str2bool(force)
		for slot in slots:
			if not force:
				self.checkIt(name, scope, tableid, adapter, enclosure,
					slot)
		for hotspare in hotspares:
			if not force:
				self.checkIt(name, scope, tableid, adapter, enclosure,
					hotspare)

		if arrayid == 'global':
			arrayid = -1
		elif arrayid == '*':
			arrayid = -2

		#
		# now add the specifications to the database
		#
		for slot in slots:
			self.db.execute("""insert into storage_controller
				(scope, tableid, adapter, enclosure, slot,
				raidlevel, arrayid, options) values ('%s', %s, %s, %s,
				%s, %s, %s, '%s') """ % (scope, tableid, adapter,
				enclosure, slot, raidlevel, arrayid, options))

		for hotspare in hotspares:
			raidlevel = -1
			if arrayid == 'global':
				arrayid = -1

			self.db.execute("""insert into storage_controller
				(scope, tableid, adapter, enclosure, slot,
				raidlevel, arrayid, options) values ('%s', %s, %s, %s,
				%s, %s, %s, '%s') """ % (scope, tableid, adapter,
				enclosure, hotspare, raidlevel, arrayid, options))

