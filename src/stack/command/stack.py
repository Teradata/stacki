#! /opt/stack/bin/python
#
# @SI_Copyright@
#                               stacki.com
#                                  v4.0
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
#	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#
# @Copyright@
#				Rocks(r)
#			 www.rocksclusters.org
#			 version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
#  
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
#  
#	"This product includes software developed by the Rocks(r)
#	Cluster Group at the San Diego Supercomputer Center at the
#	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".	 For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@

from __future__ import print_function
import warnings
warnings.filterwarnings("ignore")

import os
import pwd
import sys
import string
import syslog
import stack	# need this so we can load the stack.commands.* modules
import stack.exception
from stack.bool import str2bool
import types
import time
import shlex
from distutils.sysconfig import get_python_lib
import traceback

# Open syslog
    
syslog.openlog('SCL', syslog.LOG_PID, syslog.LOG_LOCAL0)


# Several Commands are run in the installation environment before the
# cluster database is created.	To enable this we only attempt to establish
# a database connection, if it fails it is not considered an error.


# First try to read the cluster password (for apache)

passwd = ''

try:
	file=open('/opt/stack/etc/my.cnf','r')
	for line in file.readlines():
		if line.startswith('password'):
			passwd = line.split('=')[1].strip()
			break
	file.close()
except:
	pass

try:
	host = stack.DatabaseHost
except:
	host = 'localhost'

# Now make the connection to the DB

try:
	from MySQLdb import *

	if os.geteuid() == 0:
		username = 'apache'
	else:
		username = pwd.getpwuid(os.geteuid())[0]

	# Connect over UNIX socket if it exists, otherwise go over the
	# network.

	if os.path.exists('/var/opt/stack/mysql/mysql.sock'):
		Database = connect(db='cluster',
			host='localhost',
			user=username,
			passwd='%s' % passwd,
			unix_socket='/var/opt/stack/mysql/mysql.sock',
			autocommit=True)
	else:
		Database = connect(db='cluster',
			host='%s' % host,
			user=username,
			passwd='%s' % passwd,
			port=40000,
			autocommit=True)

except ImportError:
	Database = None
except OperationalError:
	Database = None

def run_command(args):
	# Check if the stack command has been quoted.

	module = None
	if not args:
		return

	cmd = args[0].split()
	if len(cmd) > 1:
		s = 'stack.commands.%s' % '.'.join(cmd)
		try:
			__import__(s)
			module = eval(s)
			i = 1
		except:
			module = None

	# Treat the entire command line as if it were a python
	# command module and keep popping arguments off the end
	# until we get a match.	 If no match is found issue an
	# error

	if not module:
		for i in range(len(args), 0, -1):
			s = 'stack.commands.%s' % '.'.join(args[:i])
			try:
				__import__(s)
				module = eval(s)
				if module:
					break
			except ImportError:
				continue

	if not module:
		sys.stderr.write('Error - Invalid stack command "%s"\n' % args[0])
		return -1

	name = ' '.join(string.split(s, '.')[2:])

	import stack.exception

	# If we can load the command object then fall through and invoke the run()
	# method.  Otherwise the user did not give a complete command line and
	# we call the help command based on the partial command given.

	if not hasattr(module,'Command'):
		import stack.commands.list.help
		help = stack.commands.list.help.Command(Database)
		fullmodpath = s.split('.')
		submodpath  = '/'.join(fullmodpath[2:])
		try:
			help.run({'subdir': submodpath}, [])
		except stack.exception.CommandError as e:
			sys.stderr.write('%s\n' % e)
			return -1
		print(help.getText())
		return -1

	
	# Check to see if STACKDEBUG variable is set.
	# This determines if the stack trace should be
	# dumped when an exception occurs.
	
	STACKDEBUG = None
	if os.environ.has_key('STACKDEBUG'):
		STACKDEBUG = str2bool(os.environ['STACKDEBUG'])

	try:
		command = getattr(module, 'Command')(Database)
		t0 = time.time()
		rc = command.runWrapper(name, args[i:])
#		syslog.syslog(syslog.LOG_INFO, 'runtime %.3f' % (time.time() - t0))
	except stack.exception.CommandError as e:
		sys.stderr.write('%s\n' % e)
		syslog.syslog(syslog.LOG_ERR, '%s' % e)
		return -1
	except:
		# Sanitize Exceptions, and log them.
		exc, msg, tb = sys.exc_info()
		for line in traceback.format_tb(tb):
			syslog.syslog(syslog.LOG_DEBUG, '%s' % line)
			sys.stderr.write(line)
		error = '%s: %s -- %s' % (module.__name__, exc.__name__, msg)
		sys.stderr.write('%s\n' % error)
		syslog.syslog(syslog.LOG_ERR, error)
		return -1

	text = command.getText()
	if len(text) > 0:
		print(text, end='')
		if text[len(text)-1] != '\n':
			print()
	syslog.closelog()
	if rc is True:
		return 0
	return -1


if len(sys.argv) == 1:
        rc = run_command(['help'])
        sys.exit(rc)

else:
	args = sys.argv[1:]
	rc = run_command(args)
	sys.exit(rc)
