# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Command(stack.commands.CartArgumentProcessor,
	stack.commands.list.command):
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


	def getCartInfo(self, args, params):
		carts = []
		if not args:
			args = [ '%' ]	   # find all cart info
		for arg in args:
			found = False
			for (cartName, url, ) in self.db.select("""
				name, url from carts where
				name like binary %s
				""", arg):
				found = True
				carts.append({'name':cartName, 'url':url})
			if not found and arg != '%':
				raise ArgNotFound(self, arg, 'cart')

		return carts


	def run(self, params, args):
		expanded, = self.fillParams([ ('expanded', 'false') ])
		expanded = self.str2bool(expanded)
		self.beginOutput()

		try:
			carts = self.getCartInfo(args, params)
		except:
			carts = []

		for cart in carts:
		    
			# For each cart determine if it is enabled
			# in any box.
			
			boxes = []

			for row in self.db.select("""b.name from
				cart_stacks s, carts c, boxes b where
				c.name=%s and
				s.cart=c.id and s.box=b.id """
				, cart['name']):

				boxes.append(row[0])

			output = [' '.join(boxes)]
			if expanded:
				output.append(cart['url'])

			self.addOutput(cart['name'], output)

		header = ['name', 'boxes']
		if expanded:
			header.append('url')
		self.endOutput(header=header, trimOwner=False)

