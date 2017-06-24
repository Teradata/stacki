# @SI_Copyright@
#                               stacki.com
#                                  v4.0
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

import re
from copy import copy
import stack.commands
from stack.exception import *

class Command(stack.commands.Command,
	      stack.commands.OSArgumentProcessor,
	      stack.commands.ApplianceArgumentProcessor,
	      stack.commands.EnvironmentArgumentProcessor,
	      stack.commands.HostArgumentProcessor):
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

		(glob, value, shadow, force, scope) = self.fillParams([
			('attr',   None, True),
			('value',  None, True),
			('shadow', False),
			('force',  True),
			('scope',  'global'),
			])

		shadow = self.str2bool(shadow)  
		force  = self.str2bool(force)

		# All the set|add|remove attribute commands for every scope
		# go through this code and just have stubbed out code to
		# get the right arguments passed down to here.
		#
		# This keeps all the attribute stuff in one place.

		lookup = { 'global'     : { 'fn'   : lambda x=None : [],
					    'table': None },
			   'os'         : { 'fn'   : self.getOSNames, 
					    'table': 'oses' },
			   'appliance'  : { 'fn'   : self.getApplianceNames, 
					    'table': 'appliances' },
			   'environment': { 'fn'   : self.getEnvironmentNames,
					    'table': 'environments' },
			   'host'       : { 'fn'   : self.getHostnames,
					    'table': 'nodes' }}

		if scope not in lookup.keys():
			raise CommandError(self, 'invalid scope "%s"' % scope)

		if not scope == 'global' and not args:
			raise ArgRequired(self)

		# If the value is set (we are not removing attributes) do not
		# allow the attr argument to be a glob.

		if value and not re.match('^[a-zA-Z_][a-zA-Z0-9_.]*$', glob):
			raise CommandError(self, 'invalid attr name "%s"'  % glob)

		# Assume that attrs is a glob and get a list of
		# matching attributes for the scope.


		targets = lookup[scope]['fn'](args)
		if scope == 'global':
			attrs = []
		else:
			attrs = {}
			for target in targets:
				attrs[target] = []

		for row in self.call('list.attr', 
				     copy(targets) + [ 'resolve=false', 
						       'scope=%s' % scope, 
						       'attr=%s'  % glob ]):
			if scope == 'global':
				attrs.append(row['attr'])
			else:
				attrs[row[scope]].append(row['attr'])

		# If the attribute is already defined and force=False
		# complain
		#
		# 	add := force=false
		# 	set := force=true

		if not force:
			for target in attrs:
				if len(attrs[target]):
					raise CommandError(self, 'attr "%s" exists for %s' % (glob, target))

		# Before we do the insert remove any existing values, otherwise
		# we need to mess around with 'update' vs 'insert' commands.

		if scope == 'global':
			for attr in attrs:
				self.db.execute(
					"""
					delete from attributes where
					scope = '%s' and
					attr  = binary '%s'
					""" % (scope, attr))
		else:
			table = lookup[scope]['table']
			for target in targets:
				for attr in attrs[target]:
					self.db.execute(
						"""
						delete from attributes where
						scope    = '%s' and 
						scopeid  = (select id from %s where name='%s') and
						attr     = '%s'
						""" % (scope, table, target, attr))

		# If the command was called with "value=" stop here and treat the
		# command as a remove command.

		if not value:
			return
		
		
		# Figure out if this a shadow attribute and then insert into the
		# correct table.

		if shadow:
			s = "'%s'" % value
			v = 'NULL'
		else:
			s = 'NULL'
			v = "'%s'" % value
			

		if scope == 'global':
			self.db.execute(
				"""
				insert into attributes
				(scope, attr, value, shadow)
				values ('%s', '%s', %s, %s)
				""" % (scope, glob, v, s))
		else:
			table = lookup[scope]['table']
			for target in targets:
				self.db.execute(
					"""
					insert into attributes
					(scope, attr, value, shadow, scopeid)
					values (
						'%s', '%s', %s, %s,
						(select id from %s where name='%s')
					)
					""" % (scope, glob, v, s, table, target))
