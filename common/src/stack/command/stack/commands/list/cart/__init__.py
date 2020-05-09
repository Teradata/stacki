# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from stack.argument_processors.cart import CartArgProcessor
from stack.argument_processors.box import BoxArgProcessor
import stack.commands


class Command(BoxArgProcessor, CartArgProcessor, stack.commands.list.command):
	"""
	List the status of available carts.
	
	<arg optional='1' type='string' name='cart' repeat='1'>
	List of carts. This should be the cart base name (e.g., stacki, os,
	etc.). If no carts are listed, then status for all the carts are
	listed.
	</arg>

	<example cmd='list cart kernel'>		
	List the status of the kernel cart.
	</example>
	
	<example cmd='list cart'>
	List the status of all the available carts.
	</example>
	"""		


	def run(self, params, args):
		cart_args = self.get_cart_names(args)
		carts = {k: {'boxes': []} for k in cart_args}

		for box in self.get_box_names():
			for cart, _ in self.get_box_carts(box):
				if cart in cart_args:
					carts[cart]['boxes'].append(box)

		self.beginOutput()

		for cart, cart_data in carts.items():
			self.addOutput(cart, [' '.join(cart_data['boxes'])])

		header = ['name', 'boxes']
		self.endOutput(header=header, trimOwner=False)

