#! /opt/stack/bin/python
#
# Below is for testing with older versions of Rocks
#! /usr/bin/python
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
#
# $Log$
# Revision 1.30  2011/05/19 18:39:29  anoop
# reading the password file should be done correctly, with or without spaces
#
# Revision 1.29  2010/09/07 23:53:08  bruno
# star power for gb
#
# Revision 1.28  2009/05/01 19:07:08  mjk
# chimi con queso
#
# Revision 1.27  2009/04/29 00:52:24  bruno
# make sure legacy apps (insert-ethers) can connect to the new database
#
# Revision 1.26  2009/03/23 23:03:57  bruno
# can build frontends and computes
#
# Revision 1.25  2009/03/06 22:45:41  bruno
# nuke 'dbreport access' and 'dbreport machines'
#
# Revision 1.24  2008/10/18 00:56:02  mjk
# copyright 5.1
#
# Revision 1.23  2008/07/22 00:34:41  bruno
# first whack at vlan support
#
# Revision 1.22  2008/03/06 23:41:44  mjk
# copyright storm on
#
# Revision 1.21  2007/07/06 04:53:00  phil
# Same code change as in rocks command line. Allows plain old users to run dbreports
#
# Revision 1.20  2007/07/03 04:58:42  phil
# Add a password for apache access to the database.
# Randomly generate password and store in /root/.my.cnf.
# Modify stack.py and sql.py to read the password, if available
#
# Revision 1.19  2007/06/23 04:03:24  mjk
# mars hill copyright
#
# Revision 1.18  2006/09/11 22:47:23  mjk
# monkey face copyright
#
# Revision 1.17  2006/08/10 00:09:41  mjk
# 4.2 copyright
#
# Revision 1.16  2006/06/22 23:20:10  mjk
# removed unused commands dictionary
#
# Revision 1.15  2006/03/11 05:08:57  phil
# Change the way argument processing is done (perhaps move to app.py)
# This supposed to be backwards compatible with current sql-aware code like
# insert-ethers, add-extra-nic, etc.  optiucsd/src/netdb has a developing example of how this works
#
# Revision 1.14  2006/01/23 18:51:49  bruno
# insert_id() is dropped in python 2.4 (it's deprecated in 2.3)
#
# Revision 1.13  2006/01/20 22:51:14  mjk
# python 2.4 changes
#
# Revision 1.12  2006/01/16 06:49:00  mjk
# fix python path for source built foundation python
#
# Revision 1.11  2005/10/12 18:08:42  mjk
# final copyright for 4.1
#
# Revision 1.10  2005/09/16 01:02:21  mjk
# updated copyright
#
# Revision 1.9  2005/07/11 23:51:35  mjk
# use rocks version of python
#
# Revision 1.8  2005/05/27 22:08:59  bruno
# the 'added' and 'removed' plugin functions now also get the nodeid
#
# Revision 1.7  2005/05/24 21:30:10  fds
# Tweaks
#
# Revision 1.6  2005/05/24 21:21:57  mjk
# update copyright, release is not any closer
#
# Revision 1.5  2005/05/23 23:59:24  fds
# Frontend Restore
#
# Revision 1.4  2005/03/14 20:32:33  fds
# insert-ethers plugin base class. Also app_global variable accessor method.
#
# Revision 1.2  2005/03/10 01:18:21  fds
# Redoing brunos 1.2 diff that got lost. No kickstart-profiles.
#
# Revision 1.20  2004/08/13 19:58:26  fds
# Support for cluster shepherd.
#
# Revision 1.19  2004/03/25 03:15:48  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.18  2003/08/15 22:34:46  mjk
# 3.0.0 copyright
#
# Revision 1.17  2003/08/15 21:07:26  mjk
# - RC files only built one per directory (fixed)
# - Default CGI arch is native (used to be i386)
# - Added scheduler,nameservices to rocksrc.xml
# - insert-ethers know what scheduler and nameservice we use
# - I forget what else
#
# Revision 1.16  2003/08/05 21:10:50  mjk
# applet support
#
# Revision 1.15  2003/05/22 16:39:28  mjk
# copyright
#
# Revision 1.14  2003/02/17 18:43:04  bruno
# updated copyright to 2003
#
# Revision 1.13  2002/10/18 21:33:26  mjk
# Rocks 2.3 Copyright
#
# Revision 1.12  2002/10/02 18:56:43  fds
# Added close method to cleanup open database connections
#
# Revision 1.11  2002/06/28 18:15:54  mjk
# - works when database is checked in
#
# Revision 1.10  2002/02/21 21:33:28  bruno
# added new copyright
#
# Revision 1.9  2001/11/09 23:50:54  mjk
# - Post release ia64 changes
#
# Revision 1.7  2001/11/09 00:19:02  mjk
# ia64 changes
#
# Revision 1.5  2001/11/08 23:39:54  mjk
# --host changes to kcgi
#
# Revision 1.3  2001/10/24 20:23:33  mjk
# Big ass commit
#
# Revision 1.1  2001/05/16 21:44:40  mjk
# - Major changes in CD building
# - Added ip.py, sql.py for SQL oriented scripts
#

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
    from MySQLdb import *
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

