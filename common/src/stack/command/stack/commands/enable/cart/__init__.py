# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.CartArgumentProcessor,
	stack.commands.enable.command):
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

		rows = self.db.execute("""
			select * from boxes where name='%s' """ % box)
		if not rows:
			raise CommandError(self, 'unknown box "%s"' % box)
			
		for cart in self.getCartNames(args):
			enabled = False
			for row in self.db.select("""
				b.name from
				cart_stacks s, carts c, boxes b where
				c.name = '%s' and b.name = '%s' and
				s.box = b.id and s.cart = c.id
				""" % (cart, box)):

				enabled = True
				
			if not enabled:
				self.db.execute("""
					insert into cart_stacks(box, cart)
					values (
					(select id from boxes where name='%s'),
					(select id from carts where name='%s')
					)""" % (box, cart))

		# Regenerate stacki.repo
		os.system("""
			/opt/stack/bin/stack report host repo localhost | 
			/opt/stack/bin/stack report script | 
			/bin/sh
			""")

