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


import subprocess
import stack.commands


class command(stack.commands.Command):
	notifications = True

	def report(self, cmd, args=[]):
		"""
		For report commands that output XML, this method runs the command
		and processes the XML to create system files.
		"""

		p = subprocess.Popen(['/opt/stack/bin/stack', 'report', 'script'],
				     stdin=subprocess.PIPE,
				     stdout=subprocess.PIPE,
				     stderr=subprocess.PIPE)

		for row in self.call(cmd, args):
			line = '%s\n' % row['col-1']
			p.stdin.write(line.encode())
		o, e = p.communicate('')

		psh = subprocess.Popen(['/bin/sh'],
				       stdin=subprocess.PIPE,
				       stdout=subprocess.PIPE,
				       stderr=subprocess.PIPE)
		out, err = psh.communicate(o)



