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

import stack.commands


class command(stack.commands.ApplianceArgumentProcessor,
	stack.commands.dump.command):
	pass


class Command(command):
	"""
	Outputs info (as rocks commands) about the appliances defined in the
	cluster database.
	
	<arg optional='1' type='string' name='appliance' repeat='1'>
	Optional list of appliance names. If no appliance names are supplied,
	then info about all appliances is output.
	</arg>
		
	<example cmd='dump appliance'>
	Dump all known appliances.
	</example>
	"""

	def run(self, params, args):
		for app in self.getApplianceNames(args):
			self.db.execute("""
				select longname, public
				from appliances where name='%s'
				""" % app)

			(longname, pub) = self.db.fetchone()

			str = "add appliance %s " % app

			if longname:
				str += "longname=%s " % self.quote(longname)
			if pub:
				str += "public=%s" % pub
				
			self.dump(str)

