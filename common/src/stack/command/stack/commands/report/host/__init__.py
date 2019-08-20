# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

from collections import defaultdict
from collections import OrderedDict
import stack.commands
from stack.commands import Warn
import stack.text
import os.path
import shlex

class command(stack.commands.HostArgumentProcessor,
	      stack.commands.report.command):
	pass


class Command(command):
	"""
	Report the host to IP address mapping in the form suitable for
	/etc/hosts.

	<example cmd='report host'>
	Outputs data for /etc/hosts.
	</example>
	"""

	def run(self, param, args):
		text = ['<stack:file stack:name="/etc/hosts">',
			stack.text.DoNotEdit(),
			'# Site additions go in /etc/hosts.local\n']

		hosts    = defaultdict(list) # hosts->[interface ...]
		networks = defaultdict(list) # network->[interface ...]

		for interface in self.call('list.host.interface', [ 'expanded=true'] ):
			host    = interface['host']
			ip      = interface['ip']
			iface   = interface['interface']
			network = interface['network']

			if ip is None:
				Warn(f'{host} interface {iface} missing IP address')
				continue

			if network is None:
				Warn(f'{host} interface {iface} not on a network')
				continue

			if interface['aliases']:
				interface['aliases'] = interface['aliases'].split()
			else:
				interface['aliases'] = []

			hosts[host].append(interface)
			networks[network].append(interface)


		# Q: Which host interface should get the hostname entry?
		#
		# default - The default interface gets both the default route
		# and gets the hostname on its IP. Further if there is only one
		# NIC it might not be set and has to be inferred.
		#
		# shortname - The shortname option overrides the default
		# interface and grabs the hostname for its IP.

		for host, interfaces in hosts.items():
			if len(interfaces) == 1: # might not be set
				interfaces[0]['default'] = True
			default   = None
			shortname = None
			for interface in interfaces:
				if interface['default'] is True:
					default = interface
				if interface['options'] is not None:
					for option in shlex.split(interface['options']):
						if option.strip() == 'shortname':
							shortname = interface
			if shortname:	  # claim the default
				if default:
					default['default'] = False
				shortname['default'] = True



		networks[''] = [{
			'ip'       : '127.0.0.1',
			'zone'     : 'localdomain',
			'default'  : True,
			'interface': 'lo',
			'host'     : 'localhost',
			'name'     : None,
			'aliases'  : []
			}]

		for network in sorted(networks):
			text.append('')
			for i in networks[network]:
				ip        = i['ip']
				zone      = i['zone']
				default   = i['default']
				interface = i['interface']
				name      = i['name']
				host      = i['host']
				aliases   = i['aliases']

				# Abusing this a bit to behave like an ordered
				# set (which doesn't exist). The 'True'
				# assignment means nothing, only tracking keys.
				names = OrderedDict()

				if zone:
					names[f'{host}.{zone}'] = True
					if name:
						names[f'{name}.{zone}'] = True

				if default:
					names[host] = True

				if name:
					names[name] = True

				for alias in aliases:
					names[alias] = True

				text.append('%s\t%s' % (ip, ' '.join(names)))


		hostlocal = '/etc/hosts.local'
		if os.path.exists(hostlocal):
			f = open(hostlocal, 'r')
			text.append('\n# Imported from /etc/hosts.local\n')
			h = f.read()
			text.append(h)
			f.close()

		text.append('</stack:file>')
		self.beginOutput()
		self.addOutput(None, '\n'.join(text))
		self.endOutput(padChar='', trimOwner=True)

