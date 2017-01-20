# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
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


import string
import stack.commands

class Command(stack.commands.list.host.command):
	"""
	Lists the groups for a host.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, groups
	for all the known hosts is listed.
	</arg>

        <param type='string' name='group'>
        Restricts the output to only members of a group. This can be a single
        group name or a comma separated list of group names.
        </param>

	<example cmd='list host group backend-0-0'>
	List the groups for backend-0-0.
	</example>
	"""

	def run(self, params, args):

		(group,) = self.fillParams([ ('group', None) ])

                if group:
                        groups = group.split(',')
                else:
                        groups = None

		self.beginOutput()

		hosts = self.getHostnames(args)
                membership = {}
                
		for host in hosts:
                        membership[host] = []
			for row in self.db.select(
                        	"""
                                n.name, g.name from
                                groups g, memberships m, nodes n
                                where
                                n.id = m.nodeid and
                                g.id = m.groupid and
                                n.name = '%s'
                                order by g.name
                                """ % host):
                                membership[row[0]].append(row[1])
                                

                if groups:
                        for host in hosts:
                                match = []
                                for group in membership[host]:
                                        if group in groups:
                                                match.append(group)
                                if match:
                                        self.addOutput(host, string.join(match, ' '))
                else:
                        for host in hosts:
                                self.addOutput(host, string.join(membership[host], ' '))


		self.endOutput(header=['host', 'groups'], trimOwner = 0)

