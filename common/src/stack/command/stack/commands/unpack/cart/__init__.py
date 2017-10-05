# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import tarfile, bz2, lzma
import stack.commands
from stack.exception import ArgRequired, ArgUnique, CommandError, ParamRequired


class Command(stack.commands.CartArgumentProcessor,
	stack.commands.unpack.command):
	"""
	Unpack a cart into the carts directory.
	
	Assumes it was packed with "stack pack cart."

	Also assumes the cart name matches the xml
	file naming scheme.

	If your cart wasn't, don't come crying to me.

	File is uncompressed into /export/stack/carts/.

	If the cart doesn't exist, it's added to the 
	database.

	<arg type='string' name='cart'>
	The name of the cart to be created.
	</arg>

	<param type='string' name='file' required='0'>
	A bz2, xz, or gz file with your cart in it.
	</param>
	"""		
		
	def unpackCart(self, cart, cartfile, cartsdir):
		with tarfile.open(cartfile,'r:*') as tar:
			cartdir = os.path.join(cartsdir,cart)
			if self.checkCart(cartfile) == True:
				print("unpacking")
				tar.extractall(cartdir)
			else:
				print("That's no cart tarfile!")
		
		tar.close()
		return

	def checkCart(self,cartfile):
		req =  ['RPMS', 'graph', 'nodes']
		if tarfile.is_tarfile(cartfile) == True:
			with tarfile.open(cartfile,'r:*') as tar:
				files = tar.getnames()
				if set(req).issubset(set(files)) == True:
					return True
				else:
					return False

	def addCart(self,cart):
		carts = self.getCartNames('','')
		if cart not in carts:
			self.command('add.cart', [cart])
		

	def run(self, params, args):
		cartfile = self.fillParams([('file', None)])

		cartsdir = '/export/stack/carts'

		if not len(args):
			raise ArgRequired(self, 'cart')
		if len(args) > 1:
			raise ArgUnique(self, 'cart')

		if cartfile[0] == None:
                        raise ParamRequired(self, 'file')
		else:
			cartfile = cartfile[0]

		cart = args[0]
		self.addCart(cart)
		self.unpackCart(cart,cartfile,cartsdir)
