#! /opt/stack/bin/python
#
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

import os
import pwd
import string
import stack.util
import stack.app
import stack.commands

# Allow this code to work on machine that don't have mysql installed.
# We do this to allow debuging on developer machines.

hasSQL = 1
try:
	from pymysql import connect
except ImportError:
	hasSQL = 0
    

class Application(stack.app.Application):

	def __init__(self, argv=None):
		stack.app.Application.__init__(self, argv)
		if 'MYSQL_HOST' in os.environ:
			self.host	= os.environ['MYSQL_HOST']
		else:
			self.host	= 'localhost'

		self.report	= []

		self.params = {}
		self.params['db'] = ['cluster', 'database']
		self.params['password'] = ['', 'password']
		self.params['host'] = [self.host, 'host']
		self.params['user'] = ['', 'host']
		
		self.shortParamsAlias = {}
		self.shortParamsAlias['d'] = 'db'
		self.shortParamsAlias['u'] = 'user'
		self.shortParamsAlias['p'] = 'password'

		self.flags = {}
		self.flags['help'] = [0, 'print help']
		self.flags['verbose'] = [0, 'print debug info']


		self.shortFlagsAlias = {}
		self.shortFlagsAlias['v'] = 'verbose'
		self.shortFlagsAlias['h'] = 'help'

		self.db = None
		
		self.formatOptions()

   
	def extendOrReplace(self, currentList, newList):

		# this takes elements of a newList and either overwrites elements of
		# of the currentList with new values or extends the list
		# if a list element is a tuple, just compare the first element of
		# each tuple.

		currentKeys = []
		for key in currentList:
			if type(key) == type(()):
				currentKeys.append(key[0])
			else:
				currentKeys.append(key)

		for value in newList:
			if type(value) == type(()):
				compareKey = value[0]
			else:
				compareKey = value
			if compareKey in currentKeys:
				i = currentKeys.index(compareKey)
				currentList[i] = value
			else:
				currentList.append(value)			
		return currentList

	
	def formatOptions(self):

		# Create the short options
		options = []
		for key in self.shortFlagsAlias.keys():
			options.append(key)
		for key in self.shortParamsAlias.keys():
			options.append((key + ":", self.params[self.shortParamsAlias[key]][1]))

		self.getopt.s = self.extendOrReplace(self.getopt.s, options)

		# Create the long options
		options = []
		for key in self.params.keys():
			option = (key + '=', "%s" % self.params[key][1])
			options.append(option)
		for key in self.flags.keys():
			option = (key, "%s" % self.flags[key][1])
			options.append(option)

		self.getopt.l = self.extendOrReplace(self.getopt.l, options)

		return 0

	def getHost(self):
		return self.params['host'][0]
    
	def getPassword(self):
		rval = self.params['password'][0]
		if len(rval) > 0:
			return rval
		try:
			file = open('/etc/my.cnf', 'r')
			for line in file.readlines():
				l = line.split('=')
				if len(l) > 1 and l[0].strip() == "password" :
					rval = l[1].strip()
					break
			file.close()
		except:
			pass

		return rval 

	def getUsername(self):
		username = self.params['user'][0]
		if len(username) > 0:
			return username
		if os.geteuid() == 0:
			username = 'apache'
		else:
			username = pwd.getpwuid(os.geteuid())[0]
		return username

	def getDatabase(self):
		return self.params['db'][0]

	def parseArg(self, c):
		if stack.app.Application.parseArg(self, c):
			return 1
		opt, val = c
		shortopt = opt[1:len(opt)]
		if shortopt in self.shortFlagsAlias.keys():
			self.flags[self.shortFlagsAlias[shortopt]][0] = 1
		if shortopt in self.shortParamsAlias.keys():
			self.params[self.shortParamsAlias[shortopt]][0] = val

		longopt = opt[2:len(opt)]
		if longopt in self.flags.keys():
			self.flags[longopt][0] = 1
		if longopt in self.params.keys():
			self.params[longopt][0] = val

		os.environ['MYSQL_HOST'] = self.params['host'][0]

		return 0


	def connect(self):
		if hasSQL:
			self.link = connect(host='%s' % self.getHost(),
					    user='%s' % self.getUsername(),
					    db='%s' % self.getDatabase(),
					    passwd='%s' % self.getPassword(),
					    unix_socket='/var/run/mysql/mysql.sock',
					    autocommit=True)

			# This is the database cursor for the rocks command line interface
			self.db = stack.commands.DatabaseConnection(self.link)

			# This is the database cursor for the stack.sql.app interface
			# Get a database cursor which is used to manage the context of
			# a fetch operation
			if self.flags['verbose'][0]:
				print("connect:connected", self.link)
			self.cursor = self.link.cursor()
			return 1
		return 0

	def execute(self, command):
		if hasSQL:
			return self.cursor.execute(command)
		return None

	def fetchone(self):
		if hasSQL:
			return self.cursor.fetchone()
		return None

	def fetchall(self):
		if hasSQL:
			return self.cursor.fetchall()
		return None

	def insertId(self):
		"Returns the last inserted id. Useful for auto_incremented columns"
		id = None
		if hasSQL:
			id = self.cursor.lastrowid
			return id

	def close(self):
		if hasSQL:
			if self.link:
				return self.link.close()
		return None

	def __repr__(self):
		return string.join(self.report, '\n')

	def getGlobalVar(self, service, component, node=0):
		import subprocess
		import shlex

		cmd = '/opt/stack/bin/stack report host attr localhost '
		cmd += 'attr=%s_%s' % (service, component)

		p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
		value = p.stdout.readlines()[0]

		return value.strip()

	
	def getNodeId(self, host):
		"""Lookup hostname in nodes table. Host may be a name
		or an IP address. Returns None if not found."""

		# Is host already an ID?

		try:
			return int(host)
		except Exception:
			pass

		# Try by name

		self.execute(
			"""select networks.node from nodes,networks where
			networks.node = nodes.id and networks.name = "%s" and
			(networks.device is NULL or
			networks.device not like 'vlan%%') """ % (host))
		try:
			nodeid, = self.fetchone()
			return nodeid
		except TypeError:
			nodeid = None

		# Try by IP
	
		self.execute(
			"""select networks.node from nodes,networks where
			networks.node = nodes.id and networks.ip ="%s" and
			(networks.device is NULL or
			networks.device not like 'vlan%%') """ % (host))
		try:
			nodeid, = self.fetchone()
			return nodeid
		except TypeError:
			nodeid = None
	
		return nodeid






class InsertEthersPlugin:
	"""Base class for any module that wants to be notified when a node
	is added or deleted in the cluster"""

	def __init__(self, app):
		# App is a stack.sql application
		self.app = app
		# This will not be available during --update.
		self.screen = app.insertor.screen

	def update(self):
		"Regenerate your config files and reload them."
		pass

	def done(self):
		"""Called just before insert-ethers quits and nodes
		have been added or removed."""
		pass

	def added(self, nodename, nodeid):
		"""This node has been added to the cluster."""
		pass

	def removed(self, nodename, nodeid):
		"This node has been removed from the cluster"
		pass

	def changed(self, old, new):
		"Not currently used"
		pass

