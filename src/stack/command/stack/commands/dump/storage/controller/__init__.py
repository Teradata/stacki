#
# @SI_Copyright@
#                               stacki.com
#                                  v4.0
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
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
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
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
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
# @Copyright@
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

				if enclosure != None:
					cmd.append('enclosure=%s' % enclosure)
				if adapter != None:
					cmd.append('adapter=%s' % adapter)
				if slot != None and slot != []:
					cmd.append('slot=%s' % ','.join(slot))
				if raidlevel != None:
					cmd.append('raidlevel=%s' % raidlevel)
				if hotspare != None:
					cmd.append('hotspare=%s' %
						','.join(hotspare))

				cmd.append('arrayid=%s' % arrayid)

				self.dump('add storage controller %s' %
					' '.join(cmd))

	def parseit(self, scope, output):
		hosts = {}
		hosts[scope] = {}

		for o in output:
			if o['adapter'] != None:
				adapter = '%s' % o['adapter']
			else:
				adapter = None

			if o['enclosure'] != None:
				enclosure = '%s' % o['enclosure']
			else:
				enclosure = None

			if o['slot'] != None:
				slot = '%s' % o['slot']
			else:
				slot = None

			if o['raidlevel'] != None:
				raidlevel = '%s' % o['raidlevel']
			else:
				raidlevel = None

			if o['arrayid'] != None:
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

