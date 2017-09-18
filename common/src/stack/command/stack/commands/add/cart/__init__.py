# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import grp
import stat
import stack.file
import stack.commands
from stack.exception import ArgRequired, ArgUnique, CommandError


class Command(stack.commands.CartArgumentProcessor,
	stack.commands.add.command):
	"""
	Add a cart.
	
	<arg type='string' name='cart'>
	The name of the cart to be created.
	</arg>

	<param type='string' name='os'>
	The OS you wish to build a cart for (e.g., 'redhat', 'sles', 'ubuntu').
	This will create default OS-specific node and graph XML files in the
	cart.
	Default: redhat.
	</param>
	"""		

	def run(self, params, args):
		self.osname, = self.fillParams([('os', 'redhat'), ])

		if not len(args):
			raise ArgRequired(self, 'cart')
		if len(args) > 1:
			raise ArgUnique(self, 'cart')

		cart = args[0]

		for row in self.db.select("""
			* from carts where name = '%s'
			""" % cart):
			raise CommandError(self, '"%s" cart exists' % cart)

		# If the directory does not exist create it along with
		# a skeleton template.

		tree = stack.file.Tree('/export/stack/carts')
		if cart not in tree.getDirs():
			for dir in [ 'RPMS', 'nodes', 'graph' ]:
				os.makedirs(os.path.join(tree.getRoot(), cart, dir))

			cartpath = os.path.join(tree.getRoot(), cart)
			args = [ cart, cartpath ]
			self.runImplementation(self.osname, args)

		# Files were already on disk either manually created or by the
		# simple template above.
		# Add the cart to the database so we can enable it for a box

		self.db.execute("""
			insert into carts(name) values ('%s')
			""" % cart)

		# make sure apache can read all the files and directories

		gr_name, gr_passwd, gr_gid, gr_mem = grp.getgrnam('apache')

		cartpath = '/export/stack/carts/%s' % cart

		for dirpath, dirnames, filenames in os.walk(cartpath):
			try:
				os.chown(dirpath, -1, gr_gid)
			except:
				pass

			perms = os.stat(dirpath)[stat.ST_MODE]
			perms = perms | stat.S_IRGRP | stat.S_IXGRP

			#
			# apache needs to be able to write in the cart directory
			# when carts are compiled on the fly
			#
			if dirpath == cartpath:
				perms |= stat.S_IWGRP

			try:
				os.chmod(dirpath, perms)
			except:
				pass

			for file in filenames:
				filepath = os.path.join(dirpath, file)

				try:
					os.chown(filepath, -1, gr_gid)
				except:
					pass

				perms = os.stat(filepath)[stat.ST_MODE]
				perms = perms | stat.S_IRGRP

				try:
					os.chmod(filepath, perms)
				except:
					pass

