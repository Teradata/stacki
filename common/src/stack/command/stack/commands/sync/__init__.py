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

from stack.util import _exec
import stack.commands


class command(stack.commands.Command):
	def report(self, cmd, args=[]):
		"""
		For report commands that output XML, this method runs the command
		and processes the XML to create system files.
		"""

		_exec('/opt/stack/bin/stack report script | /bin/bash', shell=True, input=self.command(cmd, args))
