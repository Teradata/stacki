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
from stack.bool import *

class Plugin(stack.commands.HostArgumentProcessor, stack.commands.Plugin):

	def provides(self):
		return 'default'


	def removeInterfaces(self, host):
		output = self.owner.call('list.host.interface', [ host ])
		for v in output:
			if v['interface']:
				self.owner.call('remove.host.interface',
					[ host, 'interface=%s' % v['interface'] ])


	def run(self, args):
		hosts, interfaces = args
		existinghosts = self.getHostnames()

		for host in hosts.keys():
			#
			# add the host if it doesn't exist
			#
			if host not in existinghosts:
				args      = [ host ]
				appliance = hosts[host].get('appliance')
				rack      = hosts[host].get('rack')
				rank      = hosts[host].get('rank')
				if appliance:
					args.append('appliance=%s' % appliance)
				if rack:
					args.append('rack=%s' % rack)
				if rank:
					args.append('rank=%s' % rank)
				self.owner.call('add.host', args)

			#
			# set the host attributes that are explicitly 
			# identified in the spreadsheet
			#
			for key in hosts[host].keys():
				if key == 'boss':
					continue

				if key == 'notes':
					self.owner.call('set.host.attr',
						[ host, 'attr=motd',
						'value=%s'
						% hosts[host][key] ])
				else:
					self.owner.call('set.host.%s' % key,
						[ host, hosts[host][key] ])

			if host not in interfaces.keys():
				continue

			#
			# process the host's interface(s) 
			#

			#	
			# first remove all the existing interfaces for this
			# host
			#	
			self.removeInterfaces(host)

			for interface in interfaces[host].keys():
				ip = None
				mac = None
				subnet = None
				ifhostname = None
				channel = None
				options = None
				vlan = None
                                default = None

				if 'ip' in interfaces[host][interface].keys():
					ip = interfaces[host][interface]['ip']
				if 'mac' in interfaces[host][interface].keys():
					mac = interfaces[host][interface]['mac']
				if 'subnet' in interfaces[host][interface].keys():
					subnet = interfaces[host][interface]['subnet']
				if 'ifhostname' in interfaces[host][interface].keys():
					ifhostname = interfaces[host][interface]['ifhostname']
				if 'channel' in interfaces[host][interface].keys():
					channel = interfaces[host][interface]['channel']
				if 'options' in interfaces[host][interface].keys():
					options = interfaces[host][interface]['options']
				if 'vlan' in interfaces[host][interface].keys():
					vlan = interfaces[host][interface]['vlan']
				if 'default' in interfaces[host][interface].keys():
					default = str2bool(interfaces[host][interface]['default'])
                                else:
                                        default = False

				#
				# now add the interface
				#
				cmdparams = [ host, 'interface=%s default=%s' % (interface, default) ]
				if mac:
					cmdparams.append('mac=%s' % mac)
				if ip:
					cmdparams.append('ip=%s' % ip)
				if subnet:
    					cmdparams.append('subnet=%s' % subnet)
				if ifhostname:
					cmdparams.append('name=%s' % ifhostname)
				if vlan:
					cmdparams.append('vlan=%d' % vlan)
                                if default:
					cmdparams.append('name=%s' % host)
				if 'bond' == interface[:4]:
					cmdparams.append('module=bonding')

				self.owner.call('add.host.interface', cmdparams)

				if channel:
					cmdparams = [ host,
						'interface=%s' % interface,
						'channel=%s' % channel ]
					self.owner.call(
						'set.host.interface.channel',
						cmdparams)

				if options:
					cmdparams = [ host,
						'interface=%s' % interface,
						'options=%s' % options ]
					self.owner.call(
						'set.host.interface.options',
						cmdparams)

