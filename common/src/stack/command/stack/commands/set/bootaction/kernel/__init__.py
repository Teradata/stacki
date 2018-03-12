# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError


class Command(stack.commands.set.bootaction.command):
	"""
	Updates the kernel for a bootaction.
	<arg type='string' name='bootaction' repeat='0' optional='1'>
	Name of the bootaction that needs to be updated.
	</arg>
	
	<param type='string' name='os'>
	os type of the bootaction.
	</param>
	<param type='string' name='type'>
	type of the bootaction. Can be install or os.
	</param>
	<param type='string' name='kernel' optional='1'>
	Updated kernel value.
	</param>
	
	<example cmd='set bootaction kernel memtest kernel="memtest" type="os" os="redhat"'>
	Sets the kernel for bootaction named memtest with type="os" and os="redhat" 
	to be "memtest".
	</example>
	"""
	
	def run(self, params, args):
	
		(b_kernel, ) = self.fillParams([ ('kernel', '', True) ])
		(b_action, b_type, b_os) = self.getBootActionTypeOS(params, args)

		if not self.actionExists(b_action, b_type, b_os):
			raise CommandError(self, 'action "%s" does not exist' % b_action)

		if b_os:
			self.db.execute(
				"""
				update bootactions 
				set kernel = '%s' where
				os = (select id from oses where name = '%s') and
				bootname = (select id from bootnames where name = '%s' and type = '%s')
				""" % (b_kernel, b_os, b_action, b_type))
		else:
			self.db.execute(
				"""
				update bootactions 
				set kernel = '%s' where
				os = '0' and 
				bootname = (select id from bootnames where name = '%s' and type = '%s')
				""" % (b_kernel, b_action, b_type))
			

