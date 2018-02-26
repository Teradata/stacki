# @copyright@
# Copyright (c) 2006 - 2018 Teradata
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

	<param type='string' name='file' required='0'>
	A bz2, xz, or tgz file with your cart in it.
	</param>
	"""		
		
	def unpackCart(self, cart, cartfile, cartsdir):
		with tarfile.open(cartfile,'r:*') as tar:
			if self.checkCart(cartfile) == True:
				print("Unpacking....%s" % cart)
				tar.extractall(cartsdir)
			else:
				print("That's no cart tarfile!")
		
		tar.close()
		print("\n\nUnpacked!")
		return

	def checkCart(self,cartfile):
		req =  ['RPMS', 'graph', 'nodes']
		if tarfile.is_tarfile(cartfile) == True:
			with tarfile.open(cartfile,'r:*') as tar:
				files = tar.getmembers()
				dirs = [ os.path.split(f.name)[-1] \
					for f in files if f.isdir() == True ]
				if set(req).issubset(set(dirs)) == True:
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

		if cartfile[0] == None:
                        raise ParamRequired(self, 'file')
		else:
			cartfile = cartfile[0]

		cart = os.path.basename(cartfile).rsplit('.',1)[0]
		self.addCart(cart)
		self.unpackCart(cart,cartfile,cartsdir)
