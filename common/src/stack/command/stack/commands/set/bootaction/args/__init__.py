# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError


class Command(stack.commands.set.bootaction.command):
	"""
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
				os = '0' and 
				bootname = (select id from bootnames where name = '%s' and type = '%s')
				""" % (b_args, b_action, b_type))
			

