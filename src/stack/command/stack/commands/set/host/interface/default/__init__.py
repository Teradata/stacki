# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
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
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@

import stack.commands
from stack.exception import *

class Command(stack.commands.set.host.interface.command):
	"""
        Designates one network as the default route for a set of hosts.
        Either the interface or network paramater is required.

	<arg optional='1' repeat='1' type='string' name='host'>
	Host name.
	</arg>
	
	<param optional='0' type='string' name='interface'>
	Device name of the default interface.
 	</param>

        <param optional='0' type='string' name='network'>
 	Network name of the default interface.
 	</param>

        <param optional='0' type='bool' name='default'>
        Can be used to set the value of default to False.
        This is used to remove all default networks.
        </param>

	"""

	def run(self, params, args):

                (interface, network, default) = self.fillParams([
                        ('default', 'true'),
                        ('interface', None),
                        ('network', None),
                        ])

                default = self.str2bool(default)

		if not interface and not network:
                        raise ParamRequired(self, ('interface', 'network'))

                for host in self.getHostnames(args):
                        if network:
                                interface = self.getInterface(host, network)
                        if not interface:
                                raise CommandError(self, 'no interface for "%s" on "%s"' %
                                                (network, host))

                        if not self.verifyInterface(host, interface):
                                raise CommandError(self, 'no interface "%s" on "%s"' %
                                                (interface, host))

                        # Exclusively set the default interface by resetting
                        # all other interfaces after enabling the specified one.
                        
                        self.db.execute("""
                        	update networks net, nodes n
                                set net.main = %s
                                where
                                n.name = '%s' and net.node = n.id and
                                net.device = '%s'
                                """ % (default, host, interface))
                        if default:
                                self.db.execute("""
                        		update networks net, nodes n
                                	set net.main='False'
                                	where
                                	n.name='%s' and net.node=n.id and
                                	net.device != '%s'
                                	""" % (host, interface))
                        

