#!/opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#


import os, sys
import string, random
import subprocess
import pwd, grp

import pymysql


# Get root credentials
conf_file = open('/etc/root.my.cnf')
for line in conf_file.readlines():
	if line.startswith('password'):
		root_pass = line.split('=')[1].strip()
		break
conf_file.close()

# Connect to the database
d = pymysql.connect(user='root', db='mysql', passwd=root_pass,
	unix_socket='/var/run/mysql/mysql.sock',
	autocommit=True)

db = d.cursor()

cmd_set = []

# Drop the django user
cmd_set.append('drop user django@localhost')
cmd_set.append('drop database if exists django')

for cmd in cmd_set:
	try:
		db.execute(cmd)
	except:
		sys.stderr.write("Could not execute %s\n" % cmd)


try:
	os.unlink('/opt/stack/etc/django.my.cnf')
	os.unlink('/opt/stack/etc/django.secret')
except:
	pass
