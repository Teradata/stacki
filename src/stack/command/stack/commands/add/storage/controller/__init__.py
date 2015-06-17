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

			self.abort('disk specification %s %s already exists in the database' % ('/'.join(label), '/'.join(value)))


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
			name = 'global'
		else:
			name = args[0]

                adapter, enclosure, slot, hotspare, raidlevel, arrayid = \
			self.fillParams([ ('adapter', None), 
				('enclosure', None), ('slot', None),
				('hotspare', None), ('raidlevel', None),
				('arrayid', None) ])

		if not hotspare and not slot:
			self.abort('slot or hotspare not specified')
		if not arrayid:
			self.abort('arrayid not specified')
		if arrayid != 'global' and not raidlevel:
			self.abort('raidlevel not specified')

		if adapter:
			try:
				adapter = int(adapter)
			except:
				self.abort('adapter is not an integer')

			if adapter < 0:
				self.abort('adapter "%s" is not zero or a positive integer' % adapter)
		else:
			adapter = -1

		if enclosure:
			try:
				enclosure = int(enclosure)
			except:
				self.abort('enclosure is not an integer')

			if adapter < 0:
				self.abort('enclosure "%s" is not zero or a positive integer' % enclosure)
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
						self.abort('slot "%s" is not an integer' % s)
					if s < 0:
						self.abort('slot "%s" is not zero or a positive integer' % s)
					if s in slots:
						self.abort('slot "%s" is listed twice' % s)

				slots.append(s)

		if raidlevel:
			try:
				raidlevel = int(raidlevel)
			except:
				self.abort('raidlevel is not an integer')

			if raidlevel not in [ 0, 1, 5, 6, 10 ]:
				self.abort('raidlevel "%s" is not supported.\nSupported raidlevels are 0, 1, 5, 6, 10.' % raidlevel)

		hotspares = []
		if hotspare:
			for h in hotspare.split(','):
				try:
					h = int(h)
				except:	
					self.abort('hotspare "%s" is not an integer' % h)
				if h < 0:
					self.abort('hotspare "%s" is not a zero or positive integer' % h)
				if h in hotspares:
					self.abort('hotspare "%s" is listed twice' % h)

				hotspares.append(h)

		if arrayid in [ 'global', '*' ]:
			pass
		else:
			try:
				arrayid = int(arrayid)
			except:	
				self.abort('arrayid "%s" is not an integer' % arrayid)
			if arrayid < 1:
				self.abort('arrayid "%s" is not a positive integer' % h)

		if arrayid == 'global' and len(hotspares) == 0:
			self.abort('arrayid is "global" with no hotspares. Please supply at least one hotspare')

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
		for slot in slots:
			self.checkIt(name, scope, tableid, adapter, enclosure,
				slot)
		for hotspare in hotspares:
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
				raidlevel, arrayid) values ('%s', %s, %s, %s,
				%s, %s, %s) """ % (scope, tableid, adapter,
				enclosure, slot, raidlevel, arrayid))

		for hotspare in hotspares:
			raidlevel = -1
			if arrayid == 'global':
				arrayid = -1

			self.db.execute("""insert into storage_controller
				(scope, tableid, adapter, enclosure, slot,
				raidlevel, arrayid) values ('%s', %s, %s, %s,
				%s, %s, %s) """ % (scope, tableid, adapter,
				enclosure, hotspare, raidlevel, arrayid))

