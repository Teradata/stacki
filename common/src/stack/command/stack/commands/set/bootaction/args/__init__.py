# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError


class Command(stack.commands.set.bootaction.command):
	"""
	Updates the args for a bootaction.
        <arg type='string' name='bootaction' repeat='0' optional='1'>
        Name of the bootaction that needs to be updated.
        </arg>

        <param type='string' name='os'>
        os type of the bootaction.
        </param>
        <param type='string' name='type'>
        type of the bootaction. Can be install or os.
        </param>
        <param type='string' name='args' optional='1'>
        Updated args value.
        </param>

        <example cmd='set bootaction args headless args="ip=bootif:dhcp inst.ks=https://10.25.241.117/install/sbin/profile.cgi" type="install" os="redhat"'>
        Sets the args for bootaction named headless with type="install" and os="redhat"
        to be "ip=bootif:dhcp inst.ks=https://10.25.241.117/install/sbin/profile.cgi".
        </example>
	"""
	
	def run(self, params, args):
	
		(b_args, ) = self.fillParams([ ('args', '', True) ])
		(b_action, b_type, b_os) = self.getBootActionTypeOS(params, args)

		if not self.actionExists(b_action, b_type, b_os):
			raise CommandError(self, 'action "%s" does not exist' % b_action)

		if b_os:
			self.db.execute(
				"""
				update bootactions 
				set args = '%s' where
				os = (select id from oses where name = '%s') and
				bootname = (select id from bootnames where name = '%s' and type = '%s')
				""" % (b_args, b_os, b_action, b_type))
		else:
			self.db.execute(
				"""
				update bootactions 
				set args = '%s' where
				os is NULL and 
				bootname = (select id from bootnames where name = '%s' and type = '%s')
				""" % (b_args, b_action, b_type))
			

