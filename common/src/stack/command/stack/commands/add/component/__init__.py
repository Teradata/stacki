# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@


import stack.api
import stack.commands
from stack.exception import CommandError, ParamRequired, ArgUnique

class command(stack.commands.ComponentArgumentProcessor,
	      stack.commands.add.command):
	pass
	

class Command(stack.commands.ApplianceArgumentProcessor,
	      stack.commands.EnvironmentArgumentProcessor,
	      command):
	"""Add a new component to the cluster.

	<arg type='string' name='component'>
	The name of the component. Component names must be unique (even across
	all component types).If the component is of the standard form of
	basename-rack-rank the default values for the appliance, rack,
	and rank parameters are taken from the component name.
	</arg>

	<param type='string' name='longname'>
	Long appliance name.  If not provided and the component name is of
	the standard form the long name is taken from the basename of 
	the component.
	</param>

	<param type='string' name='rack'>
	The number of the rack where the machine is located. The convention
	in Stacki is to start numbering at 0. If not provided and the component
	name is of the standard form the rack number is taken from the component
	name.
	</param>

	<param type='string' name='rank'>
	The position of the machine in the rack. The convention in Stacki
	is to number from the bottom of the rack to the top starting at 0.
	If not provided and the component name is of the standard form the rank
	number is taken from the component name.
	</param>

	<param type='string' name='environment'>
	Name of the component environment.  For most users this is not specified.
	Environments allow you to partition components into logical groups.
	</param>

	<example cmd='add component backend-0-1'>
	Adds the component "backend-0-1" to the database with a appliance
	name of "backend", a rack number of 0, and rank of 1.
	</example>

	<example cmd='add component backend rack=0 rank=1 longname=Backend'>
	Adds the component "backend" to the database with a long appliance name
	of "Backend", a rack number of 0, and rank of 1.
	</example>

	<related>add component interface</related>

	"""

	def run(self, params, args):
		if len(args) != 1:
			raise ArgUnique(self, 'component')

		name = args[0]
		(appliance, rack, rank, environment) = self.fillParams([
			('appliance',   None),
			('rack',        None),
			('rank',        None),
			('environment', None) ])

		component = stack.api.Component()
		component.add(name, appliance, rack, rank)
		if environment:
			component.set(name, environment=environment)

			
