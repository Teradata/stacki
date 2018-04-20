# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
# 
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands


class Command(stack.commands.HostArgumentProcessor,
	stack.commands.report.command):
	"""
	Outputs the network configuration file for a host (on RHEL-based
	machines, this is the contents of the file /etc/sysconfig/network).

	<arg type='string' name='host' repeat='1'>
	Hostname.
	</arg>

	<example cmd='report host network backend-0-0'>
	Output the network configuration for backend-0-0.
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()
		
		hosts = self.getHostnames(args)

		# Get os attribute for all hosts
		a = hosts[:]
		a.append('attr=os')
		attrs = self.call('list.host.attr', a)

		for host in hosts:
			network = None
			zone    = None
			name    = None
			gateway = None

			# Get the host OS
			hoa  = list(filter(lambda x: x['host'] == host, attrs))[0]
			hostos = hoa['value']

			# Get Host Interfaces
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

			# For redhat, /etc/sysconfig/network is a file. For SuSE, it's a directory
			if hostos == 'redhat':
				self.addOutput(host, '<stack:file stack:name="/etc/sysconfig/network">')
				self.addOutput(host, 'NETWORKING=yes')
				self.addOutput(host, 'HOSTNAME=%s' % hostname)
				if gateway:
					self.addOutput(host, 'GATEWAY=%s' % gateway)
				self.addOutput(host, '</stack:file>')

			#
			# Some version require the hostname to be placed into
			# /etc/hostname
			#
			self.addOutput(host, 
				'<stack:file stack:name="/etc/hostname">')
			self.addOutput(host, '%s' % hostname)
			self.addOutput(host, '</stack:file>')

			# SuSE also requires a /etc/HOSTNAME file
			if hostos == 'sles':
				self.addOutput(host, '<stack:file stack:name="/etc/HOSTNAME">')
				self.addOutput(host, '%s' % hostname)
				self.addOutput(host, '</stack:file>')
			

		self.endOutput(padChar='', trimOwner=True)
