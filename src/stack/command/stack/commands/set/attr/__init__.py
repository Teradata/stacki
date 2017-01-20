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
#
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
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
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
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
# @Copyright@


import stack.commands
from stack.exception import *

class Command(stack.commands.Command,
              stack.commands.OSArgumentProcessor,
              stack.commands.ApplianceArgumentProcessor):
	"""
	Sets a global attribute for all nodes

	<param type='string' name='attr' optional='0'>
	Name of the attribute
	</param>

	<param type='string' name='value' optional='0'>
	Value of the attribute
	</param>
	
	<param type='boolean' name='shadow'>
	If set to true, then set the 'shadow' value (only readable by root
	and apache).
	</param>

	<example cmd='set attr attr=sge value=False'>
	Sets the sge attribution to False
	</example>

	<related>list attr</related>
	<related>remove attr</related>
	"""

	def run(self, params, args):

		(attr, value, shadow, force, scope, obj) = self.fillParams([
                        ('attr',   None, True),
                        ('value',  None, True),
			('shadow', 'n'),
			('force',  'y'),
                        ('scope',  'global'),
                        ('object', None)
                        ])

                shadow = self.str2bool(shadow)  
		force  = self.str2bool(force)

                if scope not in [ 'global',
                                  'os',
                                  'environment',
                                  'appliance',
                                  'host' ]:
                        raise CommandError(self, 'invalid scope "%s"' % scope)


                if scope == 'global':
                        lcmd  = 'list.attr'
                        rcmd  = 'remove.attr'
                        flags = []
                else:
                        if not obj:
                                raise CommandError(self, 'object not specified')
                        lcmd  = 'list.%s.attr' % scope
                        rcmd  = 'remove.%s.attr' % scope
                        flags = [ obj ]
                flags.append("attr=%s" % attr)

		if not force:
			if self.command(lcmd, flags):
                                raise CommandError(self, 'attr "%s" exists' % attr)

		self.command(rcmd, flags)
                
		if shadow:
			s = "'%s'" % value
			v = 'NULL'
		else:
			s = 'NULL'
			v = "'%s'" % value
                        
                if scope == 'os':
                        obj = self.getOSNames([obj])[0]
                        self.db.execute(
                                """
			        insert into attributes
			        (scope, attr, value, shadow, pointerstr)
			        values ('%s', '%s', %s, %s, '%s')
			        """ % (scope, attr, v, s, obj))
                elif scope == 'environment':
                        self.db.execute(
                                """
			        insert into attributes
			        (scope, attr, value, shadow, pointerstr)
			        values ('%s', '%s', %s, %s, '%s')
			        """ % (scope, attr, v, s, obj))
                elif scope == 'appliance':
                        obj = self.getApplianceNames([obj])[0]
                        self.db.execute(
                                """
			        insert into attributes
			        (scope, attr, value, shadow, pointerid)
			        values (
                                	'%s', '%s', %s, %s, 
                                	(select id from appliances where name='%s')
                                )
			        """ % (scope, attr, v, s, obj))
                elif scope == 'host':
                        obj = self.db.getHostname(obj)
                        self.db.execute(
                                """
			        insert into attributes
			        (scope, attr, value, shadow, pointerid)
			        values (
                                	'%s', '%s', %s, %s, 
                                	(select id from nodes where name='%s')
                                )
			        """ % (scope, attr, v, s, obj))
                else:
			self.db.execute(
                                """
			        insert into attributes
			        (scope, attr, value, shadow)
			        values ('%s', '%s', %s, %s)
			        """ % (scope, attr, v, s))
