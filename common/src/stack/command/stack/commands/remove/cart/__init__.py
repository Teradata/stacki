#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import os
import stack.commands
from stack.exception import ArgRequired


class Command(stack.commands.CartArgumentProcessor,
	stack.commands.remove.command):
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

	def run(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'cart')

		cartpath = '/export/stack/carts'
		for cart in self.getCartNames(args):
			os.system('/bin/rm -rf %s' % os.path.join(cartpath, cart))

			#
			# Remove cart from database
			#
			self.db.execute("delete from carts where name = '%s'"
				% cart)

		os.system("""
			/opt/stack/bin/stack report host repo localhost | 
			/opt/stack/bin/stack report script | 
			/bin/sh
			""")
