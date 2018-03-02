# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import stack.commands
from stack.exception import CommandError


class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
	Output the PXE file for a host
	<arg name="host" type="string" repeat="1">
	One or more hostnames
	</arg>
	<param name="action" type="string" optional="0">
	Generate PXE file for a specified action
	</param>
	"""


	def run(self, params, args):

		hosts = self.getHostnames(args, managed_only=True)

		(action,) = self.fillParams([
			('action', None)
		])

		ha = {}
		for host in hosts:
			ha[host] = {
				'host'       : host,
				'action'     : None,
				'type'       : action,
				'attrs'      : {}
			}


		for row in self.call('list.host.attr', hosts):
			ha[row['host']]['attrs'][row['attr']] = row['value']

		if not action: # param can override the db
			for row in self.call('list.host.boot', hosts):
				ha[row['host']]['type'] = row['action']

		for row in self.call('list.host', hosts):
			h = ha[row['host']]
			if h['type'] == 'install':
				h['action'] = row['installaction']
			elif h['type'] == 'os':
				h['action'] = row['osaction']
			h['os']        = row['os']
			h['appliance'] = row['appliance']

		ba = {}
		for row in self.call('list.bootaction'):
			ba[(row['bootaction'], row['type'], row['os'])] = row

		for host in hosts:
			h   = ha[host]
			key = (h['action'], h['type'], None)
			if key in ba:
				b = ba[key]
				h['kernel']  = b['kernel']
				h['ramdisk'] = b['ramdisk']
				h['args']    = b['args']
			key = (h['action'], h['type'], h['os'])
			if key in ba:
				b = ba[key]
				h['kernel']  = b['kernel']
				h['ramdisk'] = b['ramdisk']
				h['args']    = b['args']

		argv = []
		for host in hosts:
			argv.append(host)
		argv.append('expanded=true')
		for row in self.call('list.host.interface', argv):
			h   = ha[row['host']]
			if 'interfaces' not in h:
				h['interfaces'] = []
			if h['appliance'] == 'frontend':
				continue
			ip  = row['ip']
			pxe = row['pxe']
			interface = row['interface']
			if ip and pxe:
				h['interfaces'].append({
					'interface': interface,
					'ip'	   : ip,
					'mask'	   : row['mask'],
					'gateway'  : row['gateway']
				})


		self.beginOutput()
		self.runPlugins(ha)
		self.endOutput(padChar='', trimOwner=True)

