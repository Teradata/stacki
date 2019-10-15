# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@


import stack.commands
from stack.exception import (
	CommandError,
	ParamRequired,
	ArgUnique,
	ArgRequired,
	ArgValue,
)
from stack.util import is_valid_hostname


class command(
	stack.commands.HostArgumentProcessor,
	stack.commands.ApplianceArgumentProcessor,
	stack.commands.BoxArgumentProcessor,
	stack.commands.EnvironmentArgumentProcessor,
	stack.commands.add.command
):
	pass


class Command(command):
	"""
	Add an new host to the cluster.

	<arg type='string' name='host'>
	A single host name.  If the hostname is of the standard form of
	basename-rack-rank the default values for the appliance, rack,
	and rank parameters are taken from the hostname.
	</arg>

	<param type='string' name='appliance'>
	The appliance name for this host.
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

	<example cmd='add host backend appliance=backend rack=0 rank=1'>
	Adds the host "backend" to the database with 1 CPU, appliance type 'backend', a rack number
	of 0, and rank of 1.
	</example>

	<related>add host interface</related>

	"""

	def run(self, params, args):
		if len(args) == 0:
			raise ArgRequired(self, 'host')

		if len(args) != 1:
			raise ArgUnique(self, 'host')

		host = args[0].lower()

		if not is_valid_hostname(host):
			raise ArgValue(self, 'host', 'a valid hostname label')

		if self.db.count('(ID) from nodes where name=%s', (host,)) > 0:
			raise CommandError(self, 'host "%s" already exists in the database' % host)

		# If the name is of the form appliancename-rack-rank
		# then do the right thing and figure out the default
		# values for appliance, rack, and rank.  If the appliance
		# name is not found in the database, or the rack/rank numbers
		# are invalid do not guess any defaults.  The name is
		# either 100% used or 0% used.

		appliances = self.getApplianceNames()

		appliance = None
		rack      = None
		rank      = None

		try:
			basename, rack, rank = host.split('-')
			if basename in appliances:
				appliance = basename

		except:
			appliance = None
			rack      = None
			rank      = None

		# fillParams with the above default values
		(appliance, rack, rank, box, environment,
		 osaction, installaction) = self.fillParams([
			 ('appliance',     appliance),
			 ('rack',          rack),
			 ('rank',          rank),
			 ('box',           'default'),
			 ('environment',   ''),
			 ('osaction',      'default'),
			 ('installaction', 'default')
		])

		if not appliance:
			raise ParamRequired(self, 'appliance')

		if not rack:
			raise ParamRequired(self, 'rack')
		if not rank:
			raise ParamRequired(self, 'rank')

		if appliance not in appliances:
			raise CommandError(self, 'appliance "%s" is not in the database' % appliance)

		if box not in self.getBoxNames():
			raise CommandError(self, 'box "%s" is not in the database' % box)

		osname = None
		for row in self.call('list.box', [ box ]):
			osname = row['os']

		# Make sure the installaction and osaction both exist
		if not self.call('list.bootaction', [ installaction,
						      'type=install',
						      'os=%s' % osname
						      ]):
			raise CommandError(self,
					   '"%s" install boot action for "%s" is missing' %
					   (installaction, osname))

		if not self.call('list.bootaction', [ osaction,
						      'type=os',
						      'os=%s' % osname
						      ]):
			raise CommandError(self,
					   '"%s" os boot action for "%s" is missing' %
					   (osaction, osname))

		self.db.execute("""
			insert into nodes
			(name, appliance, box, rack, rank)
			values (
				%s,
			 	(select id from appliances where name=%s),
			 	(select id from boxes      where name=%s),
				%s, %s
			)
			""", (host, appliance, box, rack, rank))

		self.command('set.host.bootaction',
			     [ host, 'type=install', 'sync=false',
			       'action=%s' % installaction ])

		self.command('set.host.bootaction',
			     [ host, 'type=os', 'sync=false',
			       'action=%s' % osaction ])

		self.command('set.host.boot', [ host, 'action=os', 'sync=false' ])

		if environment:
			self.command('set.host.environment',
				     [ host, "environment=%s" % environment ])
