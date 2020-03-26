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

import os

import stack.commands
from stack.commands import HostArgProcessor

class command(HostArgProcessor, stack.commands.iterate.command):
	pass

	
class Command(command):
	"""
	Iterate sequentially over a list of hosts.  This is used to run 
	a shell command on the frontend with with '%' wildcard expansion for
	every host specified.
				
	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied iterate over
	all hosts except the frontend.
	</arg>

	<param optional='0' type='string' name='command'>
	The shell command to be run for each host.  The '%' character is used as
	a wildcard to indicate the hostname.  Quoting of the '%' to expand to a 
	literal is accomplished with '%%'.
	</param>
	
	<example cmd='iterate host backend command="scp file %:/tmp/"'>
	Copies file to the /tmp directory of every backend node
	</example>
	"""

	def run(self, params, args):

		(cmd, ) = self.fillParams([ ('command', None, True) ])

		self.beginOutput()

		hosts = []
		if len(args) == 0:
			#
			# no hosts are supplied. we need to exclude the frontend
			#
			for host in self.getHostnames(args):
				if host == self.db.getHostname('localhost'):
					#
					# don't include the frontend
					#
					continue

				hosts.append(host)
		else:
			hosts = self.getHostnames(args)
			
		for host in hosts:
			# Turn the wildcard '%' into the hostname, and '%%' into
			# a single '%'.

			s = ''
			prev = ''
			for i in range(0, len(cmd)):
				curr = cmd[i]
				try:
					next = cmd[i + 1]
				except:
					next = ''
				if curr == '%':
					if prev != '%' and next != '%':
						s   += host
						prev = host
						continue # consume '%'
					elif prev == '%':
						s   += '%'
						prev = '*'
						continue # consume '%'
				else:
					s += curr
				prev = curr

			os.system(s)
#			for line in os.popen(s).readlines():
#				self.addOutput(host, line[:-1])

		self.endOutput(padChar='')
