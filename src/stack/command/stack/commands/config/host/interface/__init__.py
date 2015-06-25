# @SI_Copyright@
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

import os
import re
import stack.commands
from stack.exception import *

class Command(stack.commands.config.host.command):
	"""
	!!! STACKIQ INTERNAL COMMAND ONLY !!!

	Configures host interfaces in the database.
	This command should only be called from a post section in a kickstart
	file.

	<arg type='string' name='host'>
	Host name of machine
	</arg>

	<param type='string' name='interface'>
	Interface names (e.g., "eth0"). If multiple interfaces are supplied,
	then they must be comma-separated.
	</param>

	<param type='string' name='mac'>
	MAC addresses for the interfaces. If multiple MACs are supplied,
	then they must be comma-separated.
	</param>

	<param type='string' name='module'>
	Driver modules to be loaded for the interfaces. If multiple modules
	are supplied, then they must be comma-separated.
	</param>

	<param type='string' name='flag'>
	Flags for the interfaces. If flags for multiple interfaces
	are supplied, then they must be comma-separated.
	</param>
	"""

	def run(self, params, args):
		(interface, mac, module, flag) = self.fillParams([
			('interface', None),
			('mac', None),
			('module', None),
			('flag', None) ])

		hosts = self.getHostnames(args)

		if len(hosts) != 1:
                	raise ArgUnique(self, 'host')

		host = hosts[0]

		sync_config = 0

		discovered_macs = []

		if mac:
			macs = mac.split(',')
		else:
			macs = []

		if interface:
			interfaces = interface.split(',')
		else:
			interfaces = []

		if module:
			modules = module.split(',')
		else:
			modules = []
		if flag:
			flags = flag.split(',')
		else:
			flags = []

		for i in range(0, len(macs)):
			a = (macs[i], )

			if len(interfaces) > i:
				a += (interfaces[i], )
			else:
				a += ('', )

			if len(modules) > i:
				a += (modules[i], )
			else:
				a += ('', )
			
			if len(flags) > i:
				a += (flags[i], )
			else:
				a += ('', )
			
			discovered_macs.append(a)

		#
		# make sure all the MACs are in the database
		#
		for (mac, interface, module, ks) in discovered_macs:
			rows = self.db.execute("""select mac from networks
				where mac = '%s' """ % (mac))
			if rows == 0:
				#
				# the mac is not in the database. but check
				# if the interface is already in the database.
				# if so, then we just need to set the MAC
				# for the interface.
				#
				rows = self.db.execute("""select * from
					networks where device = '%s' and
					node = (select id from nodes where
					name = '%s')""" % (interface, host))

				if rows == 1:
					self.command('set.host.interface.mac',
						(host, 'interface=%s' % interface,
						'mac=%s' % mac))
					#
					# since the MAC changed, we are not
					# guaranteed that the module will be
					# correct. we need to clear out the
					# module field
					#
					self.command(
						'set.host.interface.module',
						(host, 'interface=%s' % interface,
						'module=NULL'))
				else:
					self.command('add.host.interface', 
						(host, 'interface=%s' % interface,
						'mac=%s' % mac))

				sync_config = 1

		#
		# update the interface-to-mac mapping
		#
		for (mac, interface, module, ks) in discovered_macs:
			self.command('set.host.interface.interface', 
				(host, 'interface=%s' % interface,
					'mac=%s' % mac))

		#
		# let's see if the private interface moved
		#
		for (mac, interface, module, ks) in discovered_macs:
			if ks != 'ks':
				continue

			rows = self.db.execute("""select mac,device from
				networks where subnet = (select id from
				subnets where name = 'private') and node =
				(select id from nodes where name = '%s') """
				% (host))
				
			if rows == 1:
				(old_mac, old_interface) = self.db.fetchone()

				if old_mac != mac:
					#
					# the private network moved. swap the
					# networking info for these two
					# interfaces
					#
					self.command('swap.host.interface',
						(host, 'sync-config=no',
						'interfaces=%s,%s' %
						(old_interface, interface)))

					sync_config = 1

		if sync_config:
			self.command('sync.config')	

