# @SI_Copyright@
#                             www.stacki.com
#                                  v3.1
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

import stack.commands.set.network

class Command(stack.commands.set.network.command):
	"""
        Enables or Disables PXE for one of more networks.

        All hosts must be connected to atleast one network that has
        PXE enabled.

        <arg type='string' name='network' optional='1' repeat='1'> 
        The names of zero of more networks. If no network is specified
        the PXE is set for all existing networks.
	</arg>
	
	<param type='boolean' name='pxe' optional='0'>
        Set to True to enable PXE for the given networks.
	</param>
	
	<example cmd='set network pxe private pxe=true'>
        Enables PXE on the "private" network.
	</example>
	"""
                
        def run(self, params, args):

                (networks, pxe) = self.fillSetNetworkParams(args, 'pxe')
		pxe = self.str2bool(pxe)
                 
        	for network in networks:
			self.db.execute("""
                        	update subnets set pxe=%s where
				subnets.name='%s'
                                """ % (pxe, network))

