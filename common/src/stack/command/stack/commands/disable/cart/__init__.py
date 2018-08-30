# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.CartArgumentProcessor,
	stack.commands.disable.command):
	"""
	Disables a cart. The cart must already be copied on the
	system using the command "stack add cart".
	
	<arg type='string' name='cart' repeat='1'>
	List of carts to disable. This should be the cart base name (e.g.,
	base, hpc, kernel).
	</arg>
	
	<param type='string' name='box'>
	The name of the box in which to disable the cart. If no box is
	specified the cart is disabled for the default box.
	</param>

	<example cmd='disable cart local'>
	Disable the cart named "local".
	</example>
	
	<related>add cart</related>
	<related>enable cart</related>
	<related>list cart</related>
	"""		

	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, 'cart')

		box, = self.fillParams([ ('box', 'default') ])

		rows = self.db.execute("""
			select * from boxes where name='%s' """ % box)

		if not rows:
			raise CommandError(self, 'unknown box "%s"' % box)
		
		for cart in self.getCartNames(args):
			self.db.execute("""
				delete from cart_stacks where
				box = (select id from boxes where name='%s')
				and
				cart = (select id from carts where name='%s')
				""" % (box, cart))

		# Regenerate stacki.repo
		os.system("""
			/opt/stack/bin/stack report host repo localhost | 
			/opt/stack/bin/stack report script | 
			/bin/sh
			""")

