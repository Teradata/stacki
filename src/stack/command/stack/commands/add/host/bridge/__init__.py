# @SI_Copyright@
#                             www.stacki.com
#                                  v3.0
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

class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
	Add a bridge interface to a given host.
	<arg name="host">
	Hostname
	</arg>
	<param name="name" type="string">
	Name for the bridge interface.
	</param>
	<param name="interface" type="string">
	Physical interface to be bridged
	</param>
	<param name="network" type="string">
	Name of the network on which the physical
	device to be bridged exists.
	</param>
	<example cmd="add host bridge backend-0-0 name=cloudbr0
	network=private interface=eth0">
	This command will create a bridge called "cloudbr0", and
	attach it to physical interface eth0 and place it on the
	private network.
	</example>
	"""
	def run(self, params, args):
		(bridge, interface, network) = self.fillParams([
			('name', None, True),
			('interface',''),
			('network',''),
			])

		hosts = self.getHostnames(args)

		if not interface and not network:
                        raise ParamRequired(self, ('interface', 'network'))

		for host in hosts:
			sql = 'select nt.ip, nt.name, s.name, nt.device, nt.main, nt.options ' +\
				'from networks nt, nodes n, subnets s where '+\
				'nt.node=n.id and nt.subnet=s.id and '      +\
				'n.name="%s"' % host
			
			if network:
				sql = sql + ' and s.name="%s"' % network
			if interface:
				sql = sql + ' and nt.device="%s"' % interface

			r = self.db.execute(sql)
			if r == 0:
				raise CommandError(self, 'Could not find ' +\
				("interface %s configured on " % interface if interface else '')+\
				("network %s on " % network if network else '')+\
				"host %s" % host)
			else:
				(ip, netname, net, dev, default_if, opts) = self.db.fetchone()

			channel = bridge
			# Set ip and subnet to NULL for original device
			self.command('set.host.interface.ip',
				[host, 'interface=%s' % dev,'ip=NULL'])
			self.command('set.host.interface.network',
				[host, 'interface=%s' % dev, 'network=NULL'])
                        
			# Create new bridge interface
			a_h_i_args = [host, "interface=%s" % bridge, 'network=%s' % net,
				'name=%s' % netname]
			if ip:
				a_h_i_args.append('ip=%s' % ip)
			self.command('add.host.interface',
				a_h_i_args)
			self.command('set.host.interface.options',
				[host, 'interface=%s' % bridge, 'options=bridge'])
			# Set the original device to point to the bridge
			self.command('set.host.interface.channel',
				[host, 'interface=%s' % dev, 'channel=%s' % bridge])
			if default_if == 1:
				self.command('set.host.interface.default',
					[host, 'interface=%s' % bridge, 'default=True'])
