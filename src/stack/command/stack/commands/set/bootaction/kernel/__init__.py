# @SI_Copyright@
# @SI_Copyright@

import stack.commands
from stack.exception import *

class Command(stack.commands.set.bootaction.command):
	"""
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
			

