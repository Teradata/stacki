# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@


import stack.commands
from stack.exception import CommandError, ParamRequired, ArgUnique


class command(stack.commands.HostArgumentProcessor,
	      stack.commands.ApplianceArgumentProcessor,
	      stack.commands.BoxArgumentProcessor,
	      stack.commands.EnvironmentArgumentProcessor,
	      stack.commands.add.command):
	pass
	

class Command(command):
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

	def addHost(self, host):
		
		if host in self.getHostnames():
			raise CommandError(self, 'host "%s" already exists in the database' % host)
	
		# If the name is of the form appliancename-rack-rank
		# then do the right thing and figure out the default
		# values for appliane, rack, and rank.  If the appliance 
		# name is not found in the database, or the rack/rank numbers
		# are invalid do not guess any defaults.  The name is
		# either 100% used or 0% used.
	
		appliances = self.getApplianceNames()

		appliance = None
		rack = None
		rank = None

		try:
			basename, rack, rank = host.split('-')
			if basename in appliances:
				appliance = basename
				rack = (rack)
				rank = (rank)
		except:
			appliance = None
			rack = None
			rank = None
				
		# fillParams with the above default values
		(appliance, longname, rack, rank, box, environment,
			osaction, installaction) = \
			self.fillParams( [
				('appliance', appliance),
				('longname', None),
				('rack', rack),
				('rank', rank),
				('box', 'default'),
				('environment', ''),
				('osaction', 'default'),
				('installaction', 'default') ])

		if not longname and not appliance:
			raise ParamRequired(self, ('longname', 'appliance'))

		if rack is None:
			raise ParamRequired(self, 'rack')
		if rank is None:
			raise ParamRequired(self, 'rank')

		if longname and not appliance:
			#
			# look up the appliance name
			#
			for o in self.call('list.appliance'):
				if o['long name'] == longname:
					appliance = o['appliance']
					break

			if not appliance:
				raise CommandError(self, 'longname "%s" is not in the database' % longname)

		if appliance not in appliances:
			raise CommandError(self, 'appliance "%s" is not in the database' % appliance)

		if box not in self.getBoxNames():
			raise CommandError(self, 'box "%s" is not in the database' % box)

		# Get IDs for OS and Box
		boxid, osid = self.db.select("id, os from boxes where name='%s'" % box)[0]
		boxid = int(boxid)
		osid = int(osid)

		# Get Bootname ID matched against a triple of (bootname, boottype, OS)
		ia = self.db.select("""b.id from bootnames b, bootactions ba 
			where b.name="%s" and b.type="install" and b.id=ba.bootname
			and ba.os=%d""" %
			(installaction, osid))
		# If we can't find one, try to get one where OS is set to 0, ie.
		# common action for all OSes
		if not ia:
			ia = self.db.select("""b.id from bootnames b, bootactions ba 
				where b.name="%s" and b.type="install" and b.id=ba.bootname
				and ba.os=0"""
				% installaction)

		# If we cannot find an install action to map to, bail out
		if not ia:
			(osname,) = self.db.select("name from oses where id=%d" % osid)[0]
			raise CommandError(self, "Cannot find %s install action for OS %s" % 
					   (installaction, osname))
		installaction_id = int(ia[0][0])

		# Same logic as above. This time try to get bootaction where
		# boottype is "OS"
		oa = self.db.select("""b.id from bootnames b, bootactions ba 
			where b.name="%s" and b.type="os" and b.id=ba.bootname
			and ba.os=%d""" % 
			(osaction, osid))
		if not oa:
			oa = self.db.select("""b.id from bootnames b, bootactions ba 
				where b.name="%s" and b.type="os" and b.id=ba.bootname
				and ba.os=0""" % osaction)
		# If we cannot find an os action to map to, bail out
		if not oa:
			(osname,) = self.db.select("name from oses where id=%d" % osid)[0]
			raise CommandError(self, "Cannot find %s os action for OS %s" % 
					   (osaction, osname))

		osaction_id = int(oa[0][0])
				
		self.db.execute("""insert into nodes
			(name, appliance, box, rack, rank, osaction, installaction)
			values ('%s', (select id from appliances where name='%s'),
			%d, '%s', '%s', %d, %d) """ %
			(host, appliance, boxid, rack, rank, osaction_id, installaction_id))

		if environment:
			self.command('set.host.environment', [ host, "environment=%s" % environment ])
			

	def run(self, params, args):
		if len(args) != 1:
			raise ArgUnique(self, 'host')

		host = args[0]
		self.addHost(host)
