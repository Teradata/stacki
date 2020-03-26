# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands import CartArgProcessor


class Command(CartArgProcessor, stack.commands.list.command):
	"""
	List the status of available carts.
	
	<arg optional='1' type='string' name='cart' repeat='1'>
	List of carts. This should be the cart base name (e.g., stacki, os,
	etc.). If no carts are listed, then status for all the carts are
	listed.
	</arg>

	<param optional='0' type='string' name='expanded'>
	Include the source url of the cart.
	</param>

	<example cmd='list cart kernel'>		
	List the status of the kernel cart.
	</example>
	
	<example cmd='list cart'>
	List the status of all the available carts.
	</example>

	<example cmd='list cart expanded=True'>
	List the status of all the available carts and their source urls.
	</example>
	"""		


	def run(self, params, args):
		expanded, = self.fillParams([ ('expanded', False) ])
		expanded = self.str2bool(expanded)

		# queury all the carts (fill the cache) and hit the db once

		carts = {}
		for name, url in self.db.select('name, url from carts'):
			carts[name] = { 'url': url, 'boxes': [] }

		for name, box in self.db.select("""
			c.name, b.name from
			cart_stacks s, carts c, boxes b where
			s.cart=c.id and s.box=b.id
			"""):
			carts[name]['boxes'].append(box)


		self.beginOutput()

		for cart in self.getCartNames(args):

			output = [ ' '.join(carts[cart]['boxes']) ]

			if expanded is True:
				output.append(carts[cart]['url'])

			self.addOutput(cart, output)

		header = ['name', 'boxes']
		if expanded is True:
			header.append('url')
		self.endOutput(header=header, trimOwner=False)

