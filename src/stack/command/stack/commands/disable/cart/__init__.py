# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
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
	stack.commands.disable.command):
	"""
	Disables a cart. The cart must already be copied on the
	system using the command "stack add cart".
	
	<arg type='string' name='cart' repeat='1'>
	List of carts to disable. This should be the cart base name (e.g.,
	base, hpc, kernel).
	</arg>
	
	<param type='string' name='box'>
	The name of the box in which to disable the cart. If no box is
	specified the cart is disabled for the default box.
	</param>

	<example cmd='disable cart local'>
	Disable the cart named "local".
	</example>
	
	<related>add cart</related>
	<related>enable cart</related>
	<related>list cart</related>
	"""		

	def run(self, params, args):
                if len(args) < 1:
                        raise ArgRequired(self, 'cart')

                box, = self.fillParams([ ('box', 'default') ])

		rows = self.db.execute("""
			select * from boxes where name='%s' """ % box)

		if not rows:
                        raise CommandError(self, 'unknown box "%s"' % box)
		
		for cart in self.getCartNames(args, params):
			self.db.execute("""
				delete from cart_stacks where
				box = (select id from boxes where name='%s')
				and
				cart = (select id from carts where name='%s')
				""" % (box, cart))

		# Regenerate stacki.repo
		os.system("""
			/opt/stack/bin/stack report host yum localhost | 
			/opt/stack/bin/stack report script | 
			/bin/sh
			""")

