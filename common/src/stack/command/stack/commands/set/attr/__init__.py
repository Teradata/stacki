# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import re
from copy import copy
import stack.commands
from stack.exception import CommandError, ArgRequired


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

		if not force and scope != 'global':
			for target in attrs:
				if len(attrs[target]):
					raise CommandError(self, 'attr "%s" exists for %s' % (glob, target))
		if not force and scope == 'global' and len(attrs):
			raise CommandError(self, 'attr "%s" exists for %s' % (glob, 'global'))

		# Before we do the insert remove any existing values, otherwise
		# we need to mess around with 'update' vs 'insert' commands.

		if scope == 'global':
			for attr in attrs:
				self.db.execute(
					"""
					delete from shadow.attributes where
					scope = %s and attr = binary %s
					""", (scope, attr))
				self.db.execute(
					"""
					delete from attributes where
					scope = %s and attr = binary %s
					""", (scope, attr))
		else:
			table = lookup[scope]['table']
			for target in targets:
				for attr in attrs[target]:
					self.db.execute(
						"""
						delete from shadow.attributes where
						scope    = %%s and 
						scopeid  = (select id from %s where name=%%s) and
						attr     = %%s
						""" % table, (scope, target, attr))
					self.db.execute(
						"""
						delete from attributes where
						scope    = %%s and 
						scopeid  = (select id from %s where name=%%s) and
						attr     = %%s
						""" % table, (scope, target, attr))

		# If the command was called with "value=" stop here and treat the
		# command as a remove command.

		if not value:
			return
		
		
		if scope == 'global':
			if shadow is True:
				self.db.execute(
					"""
					insert into shadow.attributes
					(scope, attr, value)
					values (%s, %s, %s)
					""", (scope, glob, value))
			else:
				self.db.execute(
					"""
					insert into attributes
					(scope, attr, value)
					values (%s, %s, %s)
					""", (scope, glob, value))
		else:
			table = lookup[scope]['table']
			for target in targets:
				if shadow is True:
					self.db.execute(
						"""
						insert into shadow.attributes
						(scope, attr, value, scopeid)
						values (
							%%s, %%s, %%s, 
							(select id from %s where name=%%s)
						)
						""" % table, (scope, glob, value, target))
				else:
					self.db.execute(
						"""
						insert into attributes
						(scope, attr, value, scopeid)
						values (
							%%s, %%s, %%s, 
							(select id from %s where name=%%s)
						)
						""" % table, (scope, glob, value, target))
