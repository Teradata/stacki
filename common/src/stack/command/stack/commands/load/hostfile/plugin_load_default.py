# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@

import sys

from stack.bool import str2bool
import stack.commands
from stack.commands import HostArgProcessor
from stack.exception import CommandError


class Plugin(HostArgProcessor, stack.commands.Plugin):

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
		existing_memberships = {}
		existing_groups = {}
		for group in self.owner.call('list.group'):
			existing_groups[group['group']] = group['hosts']
		for member in self.owner.call('list.host.group'):
			existing_memberships[member['host']] = member['groups'].split()

		# prune group assignments for incoming hosts
		for host in hosts.keys():
			# no need to prune hosts not from the spreadsheet, or totally new hosts
			if host not in existinghosts:
				appliance    = hosts[host].get('appliance')
				if appliance == 'frontend':
					raise CommandError(self, 'Renaming frontend is not supported!')
				continue

			for group in existing_memberships[host]:
				self.owner.call('remove.host.group', [host, 'group=%s' % group])



		sys.stderr.write('\tAdd Host\n')
		for host in hosts.keys():

			sys.stderr.write('\t\t%s\r' % host)

			#
			# add the host if it doesn't exist
			#
			if host not in existinghosts:
				args         = [ host ]
				appliance    = hosts[host].get('appliance')
				box          = hosts[host].get('box')
				rack         = hosts[host].get('rack')
				rank         = hosts[host].get('rank')

				for paramName in [ 'appliance', 'box',
						   'rack', 'rank' ]:
					paramValue = hosts[host].get(paramName)
					if paramValue:
						args.append('%s=%s' %
							(paramName, paramValue))
						del hosts[host][paramName]

				self.owner.call('add.host', args)

			if 'installaction' in hosts[host]:
				self.owner.call('set.host.bootaction',
						[ host,
						  'sync=false',
						  'type=install',
						  'action=%s' % hosts[host]['installaction']
					  ])
				del hosts[host]['installaction']
			if 'osaction' in hosts[host]:
				self.owner.call('set.host.bootaction',
						[ host,
						  'sync=false',
						  'type=os',
						  'action=%s' % hosts[host]['osaction']
					  ])
				del hosts[host]['osaction']

			if 'groups' in hosts[host]:
				for groupname in hosts[host]['groups']:
					if groupname not in existing_groups:
						self.owner.call('add.group', [groupname])
						existing_groups[groupname] = None

					param = 'group=%s' % groupname
					self.owner.call('add.host.group', [host, param])
				del hosts[host]['groups']
			#
			# set the host attributes that are explicitly
			# identified in the spreadsheet
			#
			for key in hosts[host].keys():
				if key == 'boss':
					continue

				if key == 'comment':
					self.owner.call('set.host.comment',
						[ host, 'comment=%s'
						% hosts[host][key] ])
				else:
					self.owner.call('set.host.%s' % key,
						[ host, '%s=%s' % (key, hosts[host][key]) ])


			sys.stderr.write('\t\t%s\r' % (' ' * len(host)))


		#
		# process the host's interface(s)
		#

		hosts = list(interfaces.keys())

		# ensure the fronted is the first to get loaded
		_frontend = self.db.getHostname('localhost')
		for index, host in enumerate(hosts):
			if host == _frontend:
				tmp_host = hosts[0]
				hosts[0] = host
				hosts[index] = tmp_host

		argv = []
		for a in interfaces.keys():
			argv.append(a)

		if argv: # remove previous host interfaces (if any)
			argv.append('all=true')
			self.owner.call('remove.host.interface', argv)

		sys.stderr.write('\tAdd Host Interface\n')
		autoip_list = []

		for host in hosts:

			sys.stderr.write('\t\t%s\r' % host)

			for interface in interfaces[host].keys():
				ip = None
				mac = None
				network = None
				ifhostname = None
				channel = None
				options = None
				vlan = None
				default = None

				if 'ip' in interfaces[host][interface].keys():
					ip = interfaces[host][interface]['ip']
				if 'mac' in interfaces[host][interface].keys():
					mac = interfaces[host][interface]['mac']
				if 'network' in interfaces[host][interface].keys():
					network = interfaces[host][interface]['network']
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
				cmdparams = [ host,
					'unsafe=true',
					'interface=%s' % interface,
					'default=%s' % default ]
				if mac:
					cmdparams.append('mac=%s' % mac)
				if ip:
					cmdparams.append('ip=%s' % ip)
				if network:
					cmdparams.append('network=%s' % network)
				if ifhostname:
					cmdparams.append('name=%s' % ifhostname)
				if vlan:
					cmdparams.append('vlan=%d' % vlan)
				if default:
					cmdparams.append('name=%s' % host)
				if 'bond' == interface[:4]:
					cmdparams.append('module=bonding')
				if channel:
					cmdparams.append('channel=%s' % channel)
				if options:
					cmdparams.append('options=%s' % options)

				if ip != 'auto':
					self.owner.call('add.host.interface', cmdparams)
				else:
					autoip_list.append(cmdparams)

			sys.stderr.write('\t\t%s\r' % (' ' * len(host)))

		# Add interfaces with ip=AUTO at the end.
		for t in autoip_list:
			self.owner.call('add.host.interface', t)


