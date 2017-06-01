#! /opt/stack/bin/python
#
# @SI_Copyright@
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
import os
import pwd
import sys
import string
import getopt
import types
import stack.util
import stack.app
import stack.commands

# Allow this code to work on machine that don't have mysql installed.
# We do this to allow debuging on developer machines.

hasSQL = 1
try:
    from pymysql import *
except ImportError:
    hasSQL = 0


class Application(stack.app.Application):

    def __init__(self, argv=None):
        stack.app.Application.__init__(self, argv)
        self.rcfileHandler = RCFileHandler
        if os.environ.has_key('MYSQL_HOST'):
            self.host	= os.environ['MYSQL_HOST']
        else:
            self.host	= 'localhost'

        self.report     = []

	self.params={}
	self.params['db'] = ['cluster','database']
	self.params['password'] = ['','password']
	self.params['host'] = [self.host,'host']
	self.params['user'] = ['','host']

	self.shortParamsAlias ={}
	self.shortParamsAlias['d'] = 'db'
	self.shortParamsAlias['u'] = 'user'
	self.shortParamsAlias['p'] = 'password'

	self.flags={}
	self.flags['help'] = [0,'print help']
        self.flags['verbose'] = [0,'print debug info']


	self.shortFlagsAlias={}
	self.shortFlagsAlias['v'] = 'verbose'
	self.shortFlagsAlias['h'] = 'help'

	self.db = None

	self.formatOptions()

   
    def extendOrReplace(self,currentList,newList):

	# this takes elements of a newList and either overwrites elements of
	# of the currentList with new values or extends the list
	# if a list element is a tuple, just compare the first element of
	# each tuple.

	currentKeys=[]
	for key in currentList:
		if type(key) == types.TupleType:
			currentKeys.append(key[0])
		else:
			currentKeys.append(key)

	for value in newList:
		if type(value) == types.TupleType:
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
	options=[]
	for key in self.shortFlagsAlias.keys():
		options.append(key)
	for key in self.shortParamsAlias.keys():
		options.append((key+":",self.params[self.shortParamsAlias[key]][1]))

	self.getopt.s = self.extendOrReplace(self.getopt.s,options)

	# Create the long options
	options=[]
	for key in self.params.keys():
		option=( key+'=',"%s"%self.params[key][1])
		options.append(option)
	for key in self.flags.keys():
		option=( key,"%s"%self.flags[key][1])
		options.append(option)

	self.getopt.l = self.extendOrReplace(self.getopt.l,options)

	return 0

    def getHost(self):
        return self.params['host'][0]
    
    def getPassword(self):
        rval = self.params['password'][0]
	if len(rval) > 0:
		return rval
	try:
		file=open('/opt/stack/etc/my.cnf','r')
		for line in file.readlines():
			l=line.split('=')
			if len(l) > 1 and l[0].strip() == "password" :
				rval=l[1].strip()
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
	opt,val = c
	shortopt=opt[1:len(opt)]
	if shortopt in self.shortFlagsAlias.keys():
		self.flags[self.shortFlagsAlias[shortopt]][0]= 1
	if shortopt in self.shortParamsAlias.keys():
		self.params[self.shortParamsAlias[shortopt]][0]= val

	longopt=opt[2:len(opt)]
	if longopt in self.flags.keys():
		self.flags[longopt][0]= 1
	if longopt in self.params.keys():
		self.params[longopt][0]= val

        os.environ['MYSQL_HOST'] = self.params['host'][0]

        return 0


    def connect(self):
        if hasSQL:
            self.link = connect(host='%s' % self.getHost(),\
				user='%s' % self.getUsername(),\
                                db='%s' % self.getDatabase(),\
				passwd='%s' % self.getPassword(),\
				unix_socket='/var/opt/stack/mysql/mysql.sock',
				autocommit=True)

            # This is the database cursor for the rocks command line interface
            self.db = stack.commands.DatabaseConnection(self.link)

            # This is the database cursor for the stack.sql.app interface
            # Get a database cursor which is used to manage the context of
            # a fetch operation
	    if self.flags['verbose'][0]:
	    	print("connect:connected",self.link)
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

	p = subprocess.Popen(shlex.split(cmd), stdout = subprocess.PIPE)
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

	self.execute("""select networks.node from nodes,networks where
		networks.node = nodes.id and networks.name = "%s" and
		(networks.device is NULL or
		networks.device not like 'vlan%%') """ % (host))
	try:
		nodeid, = self.fetchone()
		return nodeid
	except TypeError:
		nodeid = None

	# Try by IP
	
	self.execute("""select networks.node from nodes,networks where
		networks.node = nodes.id and networks.ip ="%s" and
		(networks.device is NULL or
		networks.device not like 'vlan%%') """ % (host))
	try:
		nodeid, = self.fetchone()
		return nodeid
	except TypeError:
		nodeid = None
	
	return nodeid



class RCFileHandler(stack.app.RCFileHandler):
    
    def __init__(self, application):
        stack.app.RCFileHandler.__init__(self, application)



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

