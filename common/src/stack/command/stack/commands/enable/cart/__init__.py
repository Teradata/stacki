# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os

import stack.commands
from stack.commands import CartArgProcessor
from stack.exception import ArgRequired, CommandError

class Command(CartArgProcessor, stack.commands.enable.command):
	"""
	Enable an available cart. The cart must already be initialized on the
	system using the command "stack add cart".

	<arg type='string' name='cart' repeat='1'>
	List of carts to enable. This should be the cart base name (e.g.,
	stacki, boss, os).
	</arg>

	<param type='string' name='box'>
	The name of the box in which to enable the cart. If no box is
	specified the cart is enabled for the default box.
	</param>

	<example cmd='enable cart local'>
	Enable the cart named "local".
	</example>

	<related>add cart</related>
	<related>disable cart</related>
	<related>list cart</related>
	"""

	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, 'cart')

		(box, ) = self.fillParams([ ('box', 'default') ])

		# Make sure our box exists
		rows = self.db.select('ID from boxes where name=%s', (box,))
		if len(rows) == 0:
			raise CommandError(self, 'unknown box "%s"' % box)

		# Remember the box ID to simply queries down below
		box_id = rows[0][0]

		for cart in self.getCartNames(args):
			# If this cart isn't already in the box, add it
			if self.db.count("""
				(*) from cart_stacks s, carts c
				where c.name=%s and s.box=%s and s.cart = c.id
				""", (cart, box_id)
			) == 0:
				self.db.execute("""
					insert into cart_stacks(cart, box)
					values ((select id from carts where name=%s), %s)
					""", (cart, box_id)
				)

		# Regenerate stacki.repo
		os.system("""
			/opt/stack/bin/stack report host repo localhost |
			/opt/stack/bin/stack report script |
			/bin/sh
			""")
