# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
# 
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

import stack.commands


class Command(stack.commands.HostArgumentProcessor,
	stack.commands.report.command):
	"""
	Outputs the network configuration file for a host (on RHEL-based
	machines, this is the contents of the file /etc/sysconfig/network).

	<arg type='string' name='host' repeat='1'>
	Hostname.
	</arg>

	<example cmd='report host network compute-0-0'>
	Output the network configuration for compute-0-0.
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()
		
		hosts = self.getHostnames(args)
		for host in hosts:
			self.addOutput(host, '<stack:file stack:name="/etc/sysconfig/network">')
			self.addOutput(host, 'NETWORKING=yes')

			network = None
			zone    = None
			name    = None
			gateway = None
			for row in self.call('list.host.interface', [ host ]):
				if row['default']:
					network = row['network']
					name    = row['name']
					if not name:
						name = host

			if network:
				for row in self.call('list.network', [ network ]):
					gateway = row['gateway']
					zone    = row['zone']

			if zone:
				hostname = '%s.%s' % (name, zone)
			else:
				hostname = name
			self.addOutput(host, 'HOSTNAME=%s' % hostname)

			if gateway:
				self.addOutput(host, 'GATEWAY=%s' % gateway)

			self.addOutput(host, '</stack:file>')

			#
			# 7.x requires the hostname to be placed into
			# /etc/hostname
			#
			if stack.release == '7.x':
				self.addOutput(host, 
					'<stack:file stack:name="/etc/hostname">')
				self.addOutput(host, '%s' % hostname)
				self.addOutput(host, '</stack:file>')

		self.endOutput(padChar='', trimOwner=True)
