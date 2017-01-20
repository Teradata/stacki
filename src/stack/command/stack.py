#! /opt/stack/bin/python
#
# @SI_Copyright@
#                               stacki.com
#                                  v3.3
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
# 	 "This product includes software developed by StackIQ" 
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
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
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
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
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
# cluster database is created.  To enable this we only attempt to establish
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

class command_struct:
	def __init__(self):
		#self.name = ''
		self.isCommand = False
		self.children = {}

class RCL_Completer:
	def __init__(self):
		self.cmd_hierarchy = command_struct()
		self.cmd_path = os.path.join(get_python_lib(), 'stack/commands')
		self.module_list = []

	def populate_cmd_hierarchy(self):
		# Walk the command hierarchy
		for r, d, f in os.walk(self.cmd_path):
			# Get the relative path for a module.
			# Example: if r is
			# /opt/stack/lib/python2.6/site-packages/stack/commands/run/host
			# return run/host
			m = os.path.relpath(r, self.cmd_path)
			# If it's the current directory, ignore
			if m == '.':
				continue

			# Convert directory structure to module path
			m = m.replace('/','.')
			try:
				# Import the module
				f = __import__('stack.commands.%s' % m)
				# Get the command class from the module
				cmd_class = eval('stack.commands.%s.Command' % m)
				# If we get the Command class, and it happens to be
				# a proper class, then append it to runnable module
				# list. Otherwise, skip over it.
				if type(cmd_class) == types.ClassType:
					self.module_list.append(m)
			except:
				continue

		# For every runnable module, add it to the command hierarchy.
		# Some modules are runnable, and have children, whereas others
		# have only children. For example, run.hadoop and run.hadoop.test
		# are valid, but simply "run" isnt valid
		for mod in self.module_list:
			cur = self.cmd_hierarchy
			# Split the module string
			mod_split = mod.split('.')
			leaf_mod = mod_split[-1]
			# All parts of the module except the leaf
			for i in mod_split:
				# Create and navigate to the end of
				# the current module tree
				if not cur.children.has_key(i):
					cur.children[i] = command_struct()
				cur = cur.children[i]
				#cur.name=i
			# Set last module as a runnable command
			cur.isCommand = True
	
	# Function to traverse a subgraph of the command graph,
	# given the start of the subgraph, and a list of tokens
	# to traverse
	def traverse(self, d, tokens, incomplete, result):
		# If we've reached a leaf node, return
		if len(d.children) == 0:
			return
		# If we're not yet at the last token, keep
		# the traversal going
		if len(tokens) > 1:
			t = tokens.pop(0)
			if d.children.has_key(t):
				self.traverse(d.children[t], tokens, incomplete, result)
		# If we're at the last token in the list of tokens.
		elif len(tokens) == 1:
			t = tokens.pop(0)
			# First check if the last token is a valid token
			if d.children.has_key(t):
				cur = d.children[t]
				# If the token is valid, but is incomplete -
				# this means that the token was entered fully
				# on the command line, but no space was added
				# that means it's a valid token for completion
				if incomplete:
					result.append(t)
				# If it's complete, that means it's processed,
				# and its children may be traversed
				else:
					# Also, if token is a valid command,
					# add an empty string to the result list,
					# so that it stays valid, and does not move
					# to a child node.
					if cur.isCommand and len(cur.children) > 0:
						result.append('')
					# Move on to the child node if the token is
					# valid and complete.
					self.traverse(cur, tokens, incomplete, result)
			# if the token is not valid, check if it's a part of
			# an existing valid token, and add all of them
			else:
				for i in d.children:
					if i.startswith(t):
						result.append(i)

		# If we've finished processing all tokens, return the children
		# of the last token.
		elif len(tokens) == 0:
			for i in d.children:
				result.append(i)


	# Function that pretty prints the tree of commands that
	# can be run. This function is very similar to the traversal
	# function, and accomplishes the print using a very similar
	# recursive traversal. Meant for testing only.
	def print_mod_cmd(self, d, tokens, level):
		if len(d.children) == 0:
			return
		if len(tokens) > 0:
			t = tokens.pop(0)
			if d.children.has_key(t):
				print('  '*level, t)
				self.print_mod_cmd(d.children[t], tokens, level+1)
			else:
				for i in d.children:
					if i.startswith(t):
						print('  '*level, i)
						self.print_mod_cmd(d.children[i], [], level+1)
		else:
			for i in d.children:
				print('  '*level, i)
				self.print_mod_cmd(d.children[i], [], level+1)

	# Completer function. This function takes in a list of tokens, and
	# returns the a list of possible completions given the tokens.
	def completer(self, token, state):
		# Get the contents of the line buffer
		r = readline.get_line_buffer()
		# Check to see if the line is complete. If there is a space
		# at the end, that means that the set of tokens is complete
		if len(r) > 0 and r[-1] == ' ':
			incomplete = False
		else:
			incomplete = True
		# Get the tokens from the readline buffer.
		tokens = readline.get_line_buffer().split()
		result = []
		# traverse the command hierarchy from the top down.
		self.traverse(self.cmd_hierarchy, tokens, incomplete, result)
		# Add a space to every returned result, so that we get completed
		# tokens for the next traversal
		f = lambda x: x + ' '
		result = map(f, result)

		# Returns the results of the traversal
		return result[state]


def run_command(args):
	# Check if the stack command has been quoted.

	module = None
        if not args:
                return
        
	cmd = args[0].split()
	if len(cmd) > 1:
		s = 'stack.commands.%s' % string.join(cmd, '.')
		try:
			__import__(s)
			module = eval(s)
			i = 1
		except:
			module = None

	# Treat the entire command line as if it were a python
	# command module and keep popping arguments off the end
	# until we get a match.  If no match is found issue an
	# error

	if not module:
		for i in range(len(args), 0, -1):
			s = 'stack.commands.%s' % string.join(args[:i], '.')
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

	name = string.join(string.split(s, '.')[2:], ' ')

        import stack.exception

	# If we can load the command object then fall through and invoke the run()
	# method.  Otherwise the user did not give a complete command line and
	# we call the help command based on the partial command given.

	if not hasattr(module,'Command'):
		import stack.commands.list.help
		help = stack.commands.list.help.Command(Database)
		fullmodpath = s.split('.')
		submodpath  = string.join(fullmodpath[2:], '/')
                try:
                        help.run({'subdir': submodpath}, [])
                except stack.exception.CommandError, e:
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

# Function that runs calls the Stack Command Line Interpreter.
def run_cli(prompt):
	rcl = RCL_Completer()
	rcl.populate_cmd_hierarchy()
	
	# Setup a file to record history
	histfile = os.path.expanduser("~/.rcli_hist")

	if not os.path.exists(histfile):
		f = open(histfile, 'w')
		f.close()
	readline.read_history_file(histfile)

	# Setup tab completion
	readline.parse_and_bind("tab: complete")
	readline.set_completer(rcl.completer)

	done = 0
	# Start main rcli loop
	while not done:
		try:
			cmd = raw_input(prompt)
			readline.write_history_file(histfile)
			if cmd == 'exit':
				done = 1
			else:
				rc = run_command(shlex.split(cmd))
		except EOFError:
			print()
			done = 1
		except KeyboardInterrupt:
			print()
			done = 1

# If the command line is empty, open the stack shell
if len(sys.argv) == 1:
	# If we're piping the output through something else
	# opening the stack shell is a bad idea. Instead
	# just run help, and quit
	if not sys.stdout.isatty():
                rc = run_command(['help'])
		sys.exit(rc)
	else:
		os.environ['TERM'] = 'vt100'
		import readline
                run_cli('%s > ' % (os.path.basename(sys.argv[0])))
else:
	args = sys.argv[1:]
	rc = run_command(args)
	sys.exit(rc)
