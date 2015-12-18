# @SI_Copyright@
#                             www.stacki.com
#                                  v2.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@

import os
import stat
import time
import sys
import string
import stack.commands
from stack.exception import *


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
			
		for cart in self.getCartNames(args, params):
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
			/opt/stack/bin/stack report host yum localhost | 
			/opt/stack/bin/stack report script | 
			/bin/sh
			""")

