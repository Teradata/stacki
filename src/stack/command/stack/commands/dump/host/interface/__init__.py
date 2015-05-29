# $Id$
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
# $Log$
# Revision 1.20  2010/09/07 23:52:53  bruno
# star power for gb
#
# Revision 1.19  2010/04/20 17:22:36  bruno
# initial support for channel bonding
#
# Revision 1.18  2009/12/16 18:30:07  bruno
# make sure to save the vlan configuration for the frontend
#
# Revision 1.17  2009/06/19 21:07:32  mjk
# - added dumpHostname to dump commands (use localhost for frontend)
# - added add commands for attrs
# - dump uses add for attr (does not overwrite installer set attrs)A
# - do not dump public or private interfaces for the frontend
# - do not dump os/arch host attributes
# - fix various self.about() -> self.abort()
#
# Revision 1.16  2009/05/01 19:06:57  mjk
# chimi con queso
#
# Revision 1.15  2009/03/13 00:02:59  mjk
# - checkpoint for route commands
# - gateway is dead (now a default route)
# - removed comment rows from schema (let's see what breaks)
# - removed short-name from appliance (let's see what breaks)
# - dbreport static-routes is dead
#
# Revision 1.14  2008/10/18 00:55:49  mjk
# copyright 5.1
#
# Revision 1.13  2008/08/28 22:04:49  bruno
# can now add entries to the networks table based on MAC. previously, we could
# only add entries with interface device name.
#
# 'rocks dump' now dumps info about nodes that have a MAC address but not an
# interface device name (e.g., 'remote management' and 'power units' nodes).
#
# Revision 1.12  2008/07/22 00:34:40  bruno
# first whack at vlan support
#
# Revision 1.11  2008/03/06 23:41:36  mjk
# copyright storm on
#
# Revision 1.10  2007/07/04 01:47:37  mjk
# embrace the anger
#
# Revision 1.9  2007/07/02 17:31:06  bruno
# cleanup dump commands
#
# Revision 1.8  2007/06/26 03:19:25  bruno
# support for upgrading from rocks 4.2.1 to 4.3 (4.2.1 frontends don't have
# a 'subnets' table)
#
# Revision 1.7  2007/06/23 03:54:52  mjk
# - first pass at consistency
# - still needs some docstrings
# - argument processors take SQL wildcards
# - add cannot run twice (must use set)
# - dump does sets not just adds
#
# Revision 1.6  2007/06/19 16:42:41  mjk
# - fix add host interface docstring xml
# - update copyright
#
# Revision 1.5  2007/06/18 22:56:47  phil
# Dump command now dumps compatible commands with updated add host interface.
# Katz-style docs added
#
# Revision 1.4  2007/06/11 20:06:18  bruno
# print *all* the interfaces.
#
# don't supply info about 'None' fields.
#
# Revision 1.3  2007/06/08 03:26:24  mjk
# - plugins call self.owner.addText()
# - non-existant bug was real, fix plugin graph stuff
# - add set host cpus|membership|rack|rank
# - add list host (not /etc/hosts, rather the nodes table)
# - fix --- padding for only None fields not 0 fields
# - list host interfaces is cool works for incomplete hosts
#
# Revision 1.2  2007/06/07 21:23:04  mjk
# - command derive from verb.command class
# - default is MustBeRoot
# - list.command / dump.command set MustBeRoot = 0
# - removed plugin non-bugfix
#
# Revision 1.1  2007/06/07 16:19:10  mjk
# - add "rocks add host"
# - add "rocks dump host"
# - add "rocks dump host interface"
# - remove "rocks add host new"
# - add mysql db init script to foundation-mysql
# - more flexible hostname lookup for the command line
#

import os
import sys
import string
import stack.commands

class Command(stack.commands.dump.host.command):
	"""
	Dump the host interface information as rocks commands.
		
	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, 
	information for all hosts will be listed.
	</arg>

	<example cmd='dump host interface compute-0-0'>
	Dump the interfaces for compute-0-0.
	</example>

	<example cmd='dump host interface compute-0-0 compute-0-1'>
	Dump the interfaces for compute-0-0 and compute-0-1.
	</example>

	<example cmd='dump host interface'>
	Dump all interfaces.
	</example>
		
	<related>add host interface</related>
	"""

	def run(self, params, args):

		for host in self.getHostnames(args):
                        rows = self.db.execute("""select distinctrow
				IF(net.subnet, sub.name, NULL),
				net.device, net.mac, net.ip,
				IF(net.subnet, sub.netmask, NULL),
				net.module, net.name, net.vlanid, net.options,
				net.channel
				from nodes n, networks net, subnets sub where
				n.name='%s' and net.node=n.id and
				(net.subnet=sub.id or net.subnet is NULL)
				order by net.device""" % host )
			if rows < 1:
				continue
			for (subnet, iface, mac, ip, netmask, module, name,
				vlan, options, channel) in self.db.fetchall():
				
				if not iface:
					if mac:
						iface = mac
					else:
						continue # nothing to dump

				# If this is the frontend (localhost) do
				# not dump anything for the public and
				# private subnets.  For the extra frontend
				# interfaces do not dump the mac or
				# module.

				host = self.dumpHostname(host)
				if host == 'localhost':
					mac    = None
					module = None

					#
					# special case: we need to save vlan
					# configurations for the public and
					# private networks on the frontend
					#
					if not vlan and subnet in \
						[ 'public', 'private' ]:

						ip     = None
						name   = None
						subnet = None
						vlan   = None
						iface  = None

				if iface:
					self.dump('add host interface %s %s' % 
						(host, iface))

				set = 'set host interface %%s %s %s %%s' % \
					(host, iface)
				if ip:
					self.dump(set % ('ip', ip))
				if name:
					self.dump(set % ('name', name))
				if mac:
					self.dump(set % ('mac', mac))
				if module:
					self.dump(set % ('module', module))
				if subnet:
					self.dump(set % ('subnet', subnet))
				if vlan:
					self.dump(set % ('vlan', vlan))
				if options:
					self.dump(set % ('options',
						'options="%s"' % options))
				if channel:
					self.dump(set % ('channel', channel))

