# $Id$
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.4  2010/09/07 23:52:54  bruno
# star power for gb
#
# Revision 1.3  2010/05/27 00:11:32  bruno
# firewall fixes
#
# Revision 1.2  2010/05/07 23:13:32  bruno
# clean up the help info for the firewall commands
#
# Revision 1.1  2010/05/05 18:15:21  bruno
# all firewall list commands are done
#
#

import stack.commands


class Command(stack.commands.NetworkArgumentProcessor,
	stack.commands.list.appliance.command):
	"""
	List the firewall rules for a given appliance type.

	<arg optional='1' type='string' name='appliance' repeat='1'>
	Zero, one or more appliance names. If no appliance names are supplied,x
	the firewall rules for all the appliances are listed.
	</arg>
	"""

	def run(self, params, args):
		self.addText(self.command('list.firewall', self._argv + [ 'scope=appliance' ]))
		return self.rc
