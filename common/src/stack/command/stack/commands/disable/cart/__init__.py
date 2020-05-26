# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from stack.argument_processors.cart import CartArgProcessor
import stack.commands
import stack.deferable
from stack.exception import ArgRequired, CommandError


class Command(CartArgProcessor, stack.commands.disable.command):
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

	@stack.deferable.rewrite_frontend_repo_file
	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, 'cart')

		box, = self.fillParams([ ('box', 'default') ])

		# Make sure our box exists
		rows = self.db.select('ID, name from boxes where name=%s', (box,))
		if len(rows) == 0:
			raise CommandError(self, 'unknown box "%s"' % box)

		# Remember the box ID to simply queries down below
		box_id = rows[0][0]
		box = rows[0][1]

		for cart in self.get_cart_names(args):
			self.db.execute("""
				delete from cart_stacks where
				box=%s and cart=(select id from carts where name=%s)
				""", (box_id, cart)
			)
