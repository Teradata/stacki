#! /opt/stack/bin/python3
#
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

import atexit
import pymysql
import sys
import syslog
import getopt
import traceback
import signal
import stack
from stack.commands import get_mysql_connection
from stack.exception import CommandError


def sigint_handler(signal, frame):
	print('\nInterrupted')
	sys.exit(0)

def db_closer(db_handle):
	# dbhandle can be None during frontend install (the CLI bootstrap) and that's ok
	if db_handle is None:
		return
	try:
		db_handle.close()
	except pymysql.err.Error:
		# yolo - (handle already closed, perhaps in a forked process)
		pass


def run_command(args, debug=False):
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

	name = ' '.join(s.split('.')[2:])

	# If we can load the command object then fall through and invoke the run()
	# method.  Otherwise the user did not give a complete command line and
	# we call the help command based on the partial command given.

	if not hasattr(module, 'Command'):
		import stack.commands.list.help
		help = stack.commands.list.help.Command(db_handle)
		fullmodpath = s.split('.')
		submodpath = '/'.join(fullmodpath[2:])
		try:
			help.run({'subdir': submodpath}, [])
		except CommandError as e:
			sys.stderr.write('%s\n' % e)
			return -1
		print(help.getText())
		return -1

	try:
		command = getattr(module, 'Command')(db_handle, debug=debug)
		rc = command.runWrapper(name, args[i:])
	except CommandError as e:
		sys.stderr.write('%s\n' % e)
		syslog.syslog(syslog.LOG_ERR, '%s' % e)
		return -1
	except Exception as e:
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

	# set the SIGPIPE to the system default (instead of python default)
	# before trying to print; prevents a stacktrace when exiting a pipe'd stack command
	signal.signal(signal.SIGPIPE, signal.SIG_DFL)

	if text and len(text) > 0:
		print(text, end='')
		if text[len(text) - 1] != '\n':
			print()
	syslog.closelog()
	if rc is True:
		return 0
	return -1



# attach a prettier interrupt handler to SIGINT (ctrl-c)
signal.signal(signal.SIGINT, sigint_handler)

# Open syslog

syslog.openlog('SCL', syslog.LOG_PID, syslog.LOG_LOCAL0)


db_handle = get_mysql_connection()

atexit.register(db_closer, db_handle)

try:
	opts, args = getopt.getopt(sys.argv[1:], '', ['debug', 'help', 'version'])
except getopt.GetoptError as msg:
	sys.stderr.write("error - %s\n" % msg)
	sys.exit(1)

debug = False
rc = None
for o, a in opts:
	if o == '--debug':
		debug = True
	elif o == '--help':
		rc = run_command(['help'])
	elif o == '--version':
		rc = run_command(['report.version'])

if rc is None:
	if len(args) == 0:
		rc = run_command(['help'])
	else:
		rc = run_command(args, debug)

sys.exit(rc)
