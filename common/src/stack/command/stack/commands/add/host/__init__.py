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

from stack.exception import CommandError, ParamRequired, ArgUnique
import stack.api
import stack.commands


class command(stack.commands.add.command):
	pass
	

class Command(stack.commands.BoxArgumentProcessor,
	      command):
	"""
	Add an new host to the cluster.

	<arg type='string' name='host'>
	A single host name.  If the hostname is of the standard form of
	basename-rack-rank the default values for the appliance, rack,
	and rank parameters are taken from the hostname.
	</arg>

	<param type='string' name='longname'>
	Long appliance name.  If not provided and the host name is of
	the standard form the long name is taken from the basename of 
	the host.
	</param>

	<param type='string' name='rack'>
	The number of the rack where the machine is located. The convention
	in Stacki is to start numbering at 0. If not provided and the host
	name is of the standard form the rack number is taken from the host
	name.
	</param>

	<param type='string' name='rank'>
	The position of the machine in the rack. The convention in Stacki
	is to number from the bottom of the rack to the top starting at 0.
	If not provided and the host name is of the standard form the rank
	number is taken from the host name.
	</param>

	<param type='string' name='box'>
	The box name for the host. The default is: "default".
	</param>

	<param type='string' name='environment'>
	Name of the host environment.  For most users this is not specified.
	Environments allow you to partition hosts into logical groups.
	</param>

	<example cmd='add host backend-0-1'>
	Adds the host "backend-0-1" to the database with 1 CPU, a appliance
	name of "backend", a rack number of 0, and rank of 1.
	</example>

	<example cmd='add host backend rack=0 rank=1 longname=Backend'>
	Adds the host "backend" to the database with 1 CPU, a long appliance name
	of "Backend", a rack number of 0, and rank of 1.
	</example>

	<related>add host interface</related>

	"""

	def run(self, params, args):
		if len(args) != 1:
			raise ArgUnique(self, 'host')

		name = args[0]
		(appliance, rack, rank, environment, box, osaction, installaction) = self.fillParams([
			('appliance',     None),
			('rack',          None),
			('rank',          None),
			('environment',   None),
			('box',           'default'),
			('osaction',      'default'),
			('installaction', 'default')])

		host = stack.api.Host()
		host.add(name, appliance, rack, rank)
		host.set(name,
			 box=box, 
			 osaction=osaction, installaction=installaction)
		if environment:
			host.component.set(name, environment=environment)


			

