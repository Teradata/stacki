# $Id$
# 
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.4  2010/09/07 23:52:57  bruno
# star power for gb
#
# Revision 1.3  2010/04/14 14:40:26  bruno
# changed 'host bootaction' to 'bootaction' in the documentation portion of
# the commands
#
# Revision 1.2  2009/05/01 19:07:00  mjk
# chimi con queso
#
# Revision 1.1  2009/02/12 21:40:05  bruno
# make the bootaction global
#
#

import stack.commands
import stack.commands.set.bootaction
from stack.commands import HostArgProcessor
from stack.exception import CommandError

class Command(HostArgProcessor,
	stack.commands.set.bootaction.command,
	stack.commands.remove.command):

	"""
	Remove a boot action specification from the system.

	<arg type='string' name='action'>
	The label name for the boot action. You can see the boot action label
	names by executing: 'stack list bootaction'.
	</arg>

	<param type='string' name='type'>
	The 'type' parameter should be either 'os' or 'install'.
	</param>

	<param type='string' name='os' optional="1">
	Specify the 'os' (e.g., 'redhat', 'sles', etc.)
	</param>

	<example cmd='remove bootaction action=default type=install'>
	Remove the default bootaction for installation.
	</example>
	"""

	def run(self, params, args):
		(b_action, b_type, b_os) = self.getBootActionTypeOS(params, args)

		if not self.actionExists(b_action, b_type, b_os):
			raise CommandError(self, 'action/type/os "%s/%s/%s" does not exists' % (b_action, b_type, b_os))

		if not b_os:
			self.db.execute("""
				delete from bootactions
				where os is NULL
				and bootname=(select id from bootnames where name=%s and type=%s)
			""", (b_action, b_type))
		else:
			self.db.execute("""
				delete from bootactions
				where os=(select id from oses where name=%s)
				and bootname=(select id from bootnames where name=%s and type=%s)
			""", (b_os, b_action, b_type))
