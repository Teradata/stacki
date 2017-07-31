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
#
# $Log:$
#

from __future__ import print_function 
import stack.commands
from pymysql import *

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'database'


	def run(self, args):
		(oldhost, oldip, password) = args

		shortname = self.owner.getHostAttr('localhost',
			'Kickstart_PrivateHostname')

		print('Updating database permissions')

		#
		# get the password for the database
		#
		file = open('/opt/stack/etc/root.my.cnf','r')
		for line in file.readlines():
			if line.startswith('password'):
				passwd = line.split('=')[1].strip()
				break
		file.close()

		#
		# get a new database cursor in order to update the 'user' table
		#
		Database = connect(db = 'mysql',
			host = 'localhost',
			user = 'root',
			passwd = passwd,
			unix_socket='/var/opt/stack/mysql/mysql.sock')

		c = Database.cursor()
		c.execute("""update user set host='%s' where host='%s'""" %
			(shortname, oldhost))
		c.close()

