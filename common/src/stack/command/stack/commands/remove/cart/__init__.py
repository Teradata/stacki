#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

from stack.argument_processors.cart import CartArgProcessor
import stack.commands
import stack.deferable
from stack.exception import ArgRequired


class Command(CartArgProcessor, stack.commands.remove.command):
	"""
	Remove a cart from both the database and filesystem.	

	<arg type='string' name='cart' repeat='1'>
	List of carts. 
	</arg>
	
	<example cmd='remove cart devel'>
	Remove the cart named 'devel'.
	</example>
	
	<related>add cart</related>
	<related>enable cart</related>
	<related>disable cart</related>
	<related>list cart</related>
	"""		

	@stack.deferable.rewrite_frontend_repo_file
	def run(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'cart')

		cartpath = '/export/stack/carts'
		for cart in self.get_cart_names(args):
			self._exec(f'/bin/rm -rf {"/".join((cartpath, cart))}', shell=True)
			self.db.execute('delete from carts where name=%s', (cart,))
