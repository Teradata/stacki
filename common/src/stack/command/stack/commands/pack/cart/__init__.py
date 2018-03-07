# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import tarfile
import stack.commands
from stack.exception import *


class Command(stack.commands.CartArgumentProcessor,
	stack.commands.pack.command):
	"""
	Pack a cart into a compressed file.
	Default is tgz.

	Compressed file is output in the current 
	working directory, so don't do it in the
	cart directory you're compressing. 

	No, really, you'll be in recursive hell and
	then where will you be?
	
	GroundHog Day my friend, GroundHog Day.

	<arg type='string' name='cart'>
	The name of the cart to be compressed.
	</arg>

	<param type='string' name='compression' required='1'>
	Compression type can be gz.
	Default is gz.
	</param>

	<param type='string' name='suffix' required='1'>
	Put the suffix on the subsequent cart file.
	Default is tgz.
	</param>

	<example cmd="pack cart site-custom">
	Tars up site-custom into site-custom.tgz.
	Includes all dirs but repodata and fingerprint.

	This does NOT remove the cart from the system.
	</example>

	<related>unpack cart file=</related>
	"""		
		
	def packCart(self, cart, path, compression, suff):
		cartfile = cart + '.%s' % suff
		with tarfile.open(cartfile,'w:%s' % compression) as tar:
			os.chdir(os.path.join(path))
			if self.checkCart(path,cart) == True:
				for name in os.listdir(cart):
					if name not in [ 'fingerprint', 'repodata']:
						print('adding %s' % name)
						tar.add(cart + '/' + name)
			else:
				print("Cart has wrong directory structure.")
		
		tar.close()
		return

	def checkCart(self,path,cart):
		req = ['RPMS', 'graph', 'nodes']
		found = os.listdir(cart)
		return set(req).issubset(set(found))
		

	def run(self, params, args):
		comp, suff = self.fillParams([
			('compression', 'gz'),
			('suffix', 'tgz')
			])

		cartdir = '/export/stack/carts'

		if not len(args):
			raise ArgRequired(self, 'cart')
		if len(args) > 1:
			raise ArgUnique(self, 'cart')

		if comp not in ['gz']:
			raise ParamValue(self, 'compression', '"gz" "gz" is default.')

		cart = args[0]
		path,cart = (os.path.split(cart))

		if not path:
			path = cartdir

		if suff != 'tgz':	
			suff = suff

		self.packCart(cart,path,comp,suff)
