# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
import stack.text
import os.path


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
		self.beginOutput()
		self.addOutput(None, stack.text.DoNotEdit())
		self.addOutput(None, '#  Site additions go in /etc/hosts.local\n')
		self.addOutput(None, '127.0.0.1\tlocalhost.localdomain\tlocalhost\n')

		aliases = {}
		for row in self.call('list.host.alias'):
			host  = row['host']
			alias = row['alias']

			if host not in row:
				aliases[host] = []
			aliases[host].append(alias)
			
		zones = {}
		for row in self.call('list.network'):
			zones[row['network']] = row['zone']
	
		for row in self.call('list.host.interface'):
			ip = row['ip']
			if not ip:
				continue

			# TODO (maybe)
			#
			# The name of the interface should be the name
			# in the interface list (not from nodes
			# table).  If this doesn't exist than use the
			# name in the nodes table.  But always use the
			# zone from the networks table.
			#
			# Don't do anything right now, this has
			# implications on the dhcpd.conf, dns, and
			# spreadsheet loading, and who knows what
			# else.

			host    = row['host']
			network = row['network']
			default = row['default']

			if network:
				zone = zones[network]
			else:
				zone = None

			names = []
			if zone:
				names.append('%s.%s' % (host, zone))
			if default:
				names.append(host)
			if host in aliases:
				for alias in aliases.get(host):
					names.append(alias)

			self.addOutput(None, '%s\t%s' % (ip, ' '.join(names)))


		# Finally, add the hosts.local file to the list
		hostlocal = '/etc/hosts.local'
		if os.path.exists(hostlocal):
			f = open(hostlocal, 'r')
			self.addOutput(None, '\n# Imported from /etc/hosts.local\n')
			h = f.read()
			self.addOutput(None, h)
			f.close()
		
		self.endOutput(padChar='', trimOwner=True)
