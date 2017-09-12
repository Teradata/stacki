# $Id$
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.10  2010/09/07 23:52:56  bruno
# star power for gb
#
# Revision 1.9  2009/05/01 19:06:58  mjk
# chimi con queso
#
# Revision 1.8  2008/10/18 00:55:50  mjk
# copyright 5.1
#
# Revision 1.7  2008/03/06 23:41:37  mjk
# copyright storm on
#
# Revision 1.6  2007/07/04 01:47:38  mjk
# embrace the anger
#
# Revision 1.5  2007/06/28 19:45:44  bruno
# all the 'rocks list host' commands now have help
#
# Revision 1.4  2007/06/19 16:42:41  mjk
# - fix add host interface docstring xml
# - update copyright
#
# Revision 1.3  2007/05/31 19:35:42  bruno
# first pass at getting all the 'help' consistent on all the rocks commands
#
# Revision 1.2  2007/05/10 20:37:01  mjk
# - massive rocks-command changes
# -- list host is standardized
# -- usage simpler
# -- help is the docstring
# -- host groups and select statements
# - added viz commands
#
# Revision 1.1  2007/04/30 17:46:03  bruno
# drop the 's' -- it makes the commands easier to use. for example, this type
# of interaction will be common:
#
#     # rocks list host partition compute-0-0
#     # rocks remove host partition compute-0-0 /var
#
# or:
#
#     # rocks list host interface compute-0-0
#     # rocks add host interface compute-0-0 if=eth1 ...
#
# by dropping the 's', we can use bash history and only change the verb and
# not also have to change 'interfaces' to 'interface'
#
# Revision 1.1  2007/04/24 17:58:09  bruno
# consist look and feel for all 'list' commands
#
# put partition commands under 'host'
#
# Revision 1.1  2007/04/05 20:51:55  bruno
# rocks-partition is now in the command line
#
#

import stack.commands


class Command(stack.commands.list.host.command):
	"""
	Lists the partitions for hosts. For each host supplied on the command
	line, this command prints the hostname and partitions for that host.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='list host partition compute-0-0'>
	List partition info for compute-0-0.
	</example>

	<example cmd='list host partition'>
	List partition info for known hosts.
	</example>
	"""

	def run(self, params, args):
	
		self.beginOutput()
		
		for host in self.getHostnames(args):
			self.db.execute("""select 
				p.device, p.mountpoint, p.uuid, p.sectorstart,
				p.partitionsize, p.partitionid, p.fstype,
				p.partitionflags, p.formatflags from 
				partitions p, nodes n where 
				n.name='%s' and n.id=p.node order by device""" %
				host)

			for row in self.db.fetchall():
				self.addOutput(host, row)

		self.endOutput(header=['host', 'device', 'mountpoint', 'uuid',
			'start', 'size', 'id', 'type', 'flags', 'formatflags'])


