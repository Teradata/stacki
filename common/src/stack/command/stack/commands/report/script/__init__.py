# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import ast
import sys
import subprocess
import stack.commands
import stack.gen


class Command(stack.commands.report.command):
	"""
	Take STDIN XML input and create a shell script that can be executed
	on a host.

	<param optional='1' type='string' name='os'>
	The OS type.
	</param>

	<param optional='1' type='string' name='arch'>
	The architecture type.
	</param>

	<param optional='1' type='string' name='attrs'>
	Attributes to be used while building the output shell script.
	</param>

	<example cmd='report host interface backend-0-0 | stack report script'>
	Take the network interface XML output from 'stack report host interface'
	and create a shell script.
	</example>
	"""

	def run(self, params, args):
		osname, attrs = self.fillParams([
			('os', self.os),
			('attrs', {}) ])

		xml = ''

		if attrs:
			attrs = ast.literal_eval(attrs)
			xml += '<!DOCTYPE stacki-profile [\n'
			for (k, v) in attrs.items():
				xml += '\t<!ENTITY %s "%s">\n' % (k, v)
			xml += ']>\n'

		xml += '<stack:profile '
		xml += 'stack:os="%s" ' % osname
		xml += 'xmlns:stack="http://www.stacki.com" '
		xml += 'stack:attrs="%s">\n' % attrs
		xml += '<stack:script stack:stage="install-post">\n'

		for line in sys.stdin.readlines():
			xml += line

		xml += '</stack:script>\n'
		xml += '</stack:profile>\n' 

		p = subprocess.Popen('/opt/stack/bin/stack list host profile chapter=main profile=bash',
				     stdin=subprocess.PIPE,
				     stdout=subprocess.PIPE,
				     stderr=subprocess.PIPE, shell=True)
		p.stdin.write(xml.encode())
		(o, e) = p.communicate()
		if p.returncode == 0:
			sys.stdout.write(o.decode())
		else:
			sys.stderr.write(e.decode())



