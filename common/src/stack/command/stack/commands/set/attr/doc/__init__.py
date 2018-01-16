# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError


class Command(stack.commands.Command):
	"""
	Changes a string containing documention for an attribute

	<param type='string' name='attr' optional='0'>
	Name of the attribute
	</param>

	<param type='string' name='doc' optional='0'>
	Documentation of the attribute
	</param>
	
	<example cmd='set attr doc attr="ssh.use_dns" doc="hosts with ssh.use_dns == True will enable DNS lookups in sshd config."'>
	Sets the documentation string for 'ssh.use_dns'
	</example>

	<related>list attr doc</related>
	<related>set attr</related>
	"""


	def run(self, params, args):

		(attr, doc) = self.fillParams([
			('attr', None, True),
			('doc',  None, True),
			])

		rows = self.db.execute("""
			select attr from attributes where attr='%s'
			""" % (attr))

		if not rows:
			raise CommandError(self, 'Cannot set documentation for a non-existant attribute')

		self.db.execute("""
			delete from attributes_doc where attr='%s'
			""" % (attr))

		if doc:
			self.db.execute(
				"""
				insert into attributes_doc
				(attr, doc)
				values ('%s', '%s')
				""" % (attr, doc))
