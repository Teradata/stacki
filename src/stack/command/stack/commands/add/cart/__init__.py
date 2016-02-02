# @SI_Copyright@
#                             www.stacki.com
#                                  v3.0
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
import sys
import grp
import stat
import string
import stack.file
import stack.commands
from stack.exception import *

class Command(stack.commands.CartArgumentProcessor,
	stack.commands.add.command):
	"""
        Add a cart.
	
	<arg type='string' name='cart'>
        The name of the cart to be created.
	</arg>
	"""		

	def run(self, params, args):
                if not len(args):
                        raise ArgRequired(self, 'cart')
                if len(args) > 1:
                        raise ArgUnique(self, 'cart')

                cart = args[0]

                for row in self.db.select("""
                        * from carts where name = '%s'
                        """ % cart):
                        raise CommandError(self, '"%s" cart exists' % cart)

                # If the directory does not exist create it along with
                # a skeleton template.
                
                tree = stack.file.Tree('/export/stack/carts')
                if not cart in tree.getDirs():
                	for dir in [ 'RPMS', 'nodes', 'graph' ]:
                		os.makedirs(os.path.join(tree.getRoot(), cart, dir))
                                
                        graph = open(os.path.join(tree.getRoot(), cart, 'graph', 'cart-%s.xml' % cart), 'w')
                        graph.write("""<?xml version="1.0" standalone="no"?>
<graph>

	<description>
        %s cart
	</description>

        <order head="backend" tail="cart-%s-backend"/>
        <edge  from="backend"   to="cart-%s-backend"/>

</graph>
""" % (cart, cart, cart))
                        graph.close()
                        
                        node = open(os.path.join(tree.getRoot(), cart, 'nodes', 'cart-%s-backend.xml' % cart), 'w')
                        node.write("""<?xml version="1.0" standalone="no"?>
<kickstart>

	<description>
        %s cart backend appliance extensions
	</description>

        <!-- <package></package> -->

<!-- shell code for post RPM installation -->
<post>

</post>
</kickstart>
""" % cart)
                        node.close()
                        

                # Files were already on disk either manually created or by the
                # simple template above.
                # Add the cart to the database so we can enable it for a box

                self.db.execute("""
                	insert into carts(name) values ('%s')
                        """ % cart)

		# make sure apache can read all the files and directories

		gr_name, gr_passwd, gr_gid, gr_mem = grp.getgrnam('apache')

                cartpath = '/export/stack/carts/%s' % cart

		for dirpath, dirnames, filenames in os.walk(cartpath):
			try:
				os.chown(dirpath, -1, gr_gid)
			except:
				pass

			perms = os.stat(dirpath)[stat.ST_MODE]
			perms = perms | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP

			#
			# apache needs to be able to write in the cart directory
			# when carts are compiled on the fly
			#
			if dirpath == cartpath:
				perms |= stat.S_IWGRP

			try:
				os.chmod(dirpath, perms)
			except:
				pass

			for file in filenames:
				filepath = os.path.join(dirpath, file)

				try:
					os.chown(filepath, -1, gr_gid)
				except:
					pass

				perms = os.stat(filepath)[stat.ST_MODE]
				perms = perms | stat.S_IRGRP

				try:
					os.chmod(filepath, perms)
				except:
					pass

