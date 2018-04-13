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

# Generate a random password for django
p = subprocess.Popen("/opt/stack/sbin/gen_random_pw",
	stdout = subprocess.PIPE,
	stderr = subprocess.PIPE)
o, e = p.communicate()
django_pass = o.strip()

# Create the Django.my.cnf file
django_conf_file = "/opt/stack/etc/django.my.cnf"
f = open(django_conf_file, 'w+')
f.write("""[client]
user		= django
port		= 40000
socket		= /var/run/mysql/mysql.sock
password	= %s
""" % django_pass)
# Set owner and group to root:apache
apache_gid = grp.getgrnam('apache')[2]
os.fchown(f.fileno(), 0, apache_gid)
f.close()

# Password access for django
cmd_set.append('create user "django"@"localhost" identified by "%s"' % django_pass)

# Create the Django Database
cmd_set.append('create database django')

# Grant django user access to the Django database
cmd_set.append('grant all on django.* to "django"@"localhost";')

for cmd in cmd_set:
	try:
		db.execute(cmd)
	except:
		sys.stderr.write("Could not execute %s\n" % cmd)

