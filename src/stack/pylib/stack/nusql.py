#! /opt/stack/bin/python
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
# Revision 1.10  2010/09/07 23:53:08  bruno
# star power for gb
#
# Revision 1.9  2009/05/01 19:07:08  mjk
# chimi con queso
#
# Revision 1.8  2008/10/18 00:56:02  mjk
# copyright 5.1
#
# Revision 1.7  2008/03/06 23:41:44  mjk
# copyright storm on
#
# Revision 1.6  2007/06/23 04:03:24  mjk
# mars hill copyright
#
# Revision 1.5  2006/09/11 22:47:23  mjk
# monkey face copyright
#
# Revision 1.4  2006/08/10 00:09:41  mjk
# 4.2 copyright
#
# Revision 1.3  2006/07/21 04:25:06  phil
# Remove diagnostic print
#
# Revision 1.2  2006/07/21 02:50:53  phil
# rocks-pxe helper function support
#
# Revision 1.1  2006/07/20 23:02:49  phil
# Derived from sql.py. Using this for newer applications that interface with the
# DB. Older apps are derived directly from sql.py and hence cannot be affected by
# methds in the class
#

from __future__ import print_function
import os
import sys
import string
import getopt
import types
import stack.util
import stack.app
import stack.sql
import gmon.encoder

class Application(stack.sql.Application):
	def __init__(self, argv):
		stack.sql.Application.__init__(self, argv)

		self.params['name'] = ['', 'node name (must be unique)']
		self.params['nodes'] = ['','node list expression']
		self.params['group'] = ['','Appliance Group']
		self.flags['dryrun'] = [0, 'only show commands']

		self.shortParamsAlias['g'] = 'group'

		self.commands={}
		self.commands['add'] = 0
		self.commands['delete'] = 0
		self.commands['dump'] = 0
		self.commands['list'] = 0
		self.commands['update'] = 0

		#
		# Table/Field Associations mapping
		#	Describes table and associate field names. These 
		#	match the SQL database 
		#
		self.tables= {}
		# Example: self.tables['pxe'] = ['node','config','bootimg']
		self.tables['nodes'] = ['name','id']

		#
		# Parameters-to-Field mapping
		#	describes SQL style mapping of command-line parameters
		#		to sql table.field
		#
		self.paramMap = {}
		# Example: self.paramMap['node'] = 'pxe.node'
		self.paramMap['name'] = 'nodes.name'

		self.dbvalues={}

		self.nodelist = ['']

		# The node list encoder/decoder.
                self.e = gmon.encoder.Encoder()

		self.formatOptions()


	def usageTail(self):
		
		cmdkeys = self.commands.keys()
		cmdstr=" <"+ cmdkeys[0] 
                for i in range(1, len(cmdkeys)):
			cmdstr = cmdstr+ "|" +  cmdkeys[i] 
		return cmdstr+'>'	
		
	# ------------------   GENERIC Helper Functions ---------------------

	def getNodeId(self,host):
		query = 'select ID from nodes where Name="%s"' % host 
		self.runQuery("nusql.getNodeId", query)
		row = self.fetchone()
		if row:
			id = row[0]
			return id
		else:
			print("Node  %s does not exist!" % host) 
			sys.exit(-1)

	#
	# fillNodeList
	#
	#
	def fillNodelist(self):
		if self.params['nodes'][0] != '' :
                        self.nodelist = \
			string.split(self.e.decode(self.params['nodes'][0]), " ")
		elif self.params['group'][0] != '' :
			query = "select nodes.name from nodes,memberships where "\
				"nodes.membership=memberships.id and " \
				"memberships.name=\'%s\'" % self.params['group'][0]
			self.runQuery("fillNodeList",query)
			self.nodelist = []	
			for row in self.fetchall():
				self.nodelist.extend([row[0]])
			if len(self.nodelist) == 0:
				self.nodelist = ['']
		elif self.params['name'][0] != '':
			self.nodelist = [self.params['name'][0]]
		else:
			self.nodelist = ['']
	
		if self.flags['verbose'][0]:
			print("node list is: ", self.nodelist)
	#
	# selectString -- if table is empty, then match all 
	#    Formats a string suitable for: 
	#	select <selectString> from ...
  	#           

	def selectString(self, table=''):
		tNames = self.tables.keys()
		outstring = ''	
		for tN in tNames:
			if table == '' or tN == table:
				for fname in self.tables[tN]:
					if outstring != '':
						outstring += ","
					outstring = outstring + tN + "." + fname
		return outstring


	#
	# fieldString
	#    Formats a string suitable for: 
	#	insert into table(<fieldString>) values( .... ) 
  	#           

	def fieldString(self, table):
		outstring = ''
		for pName in self.params.keys():
			tN = ''
			if pName in self.paramMap.keys():
				tN,fN = self.paramMap[pName].split('.')
			if tN == table:
				if outstring != '':
					outstring += ","
				outstring += fN 
		return outstring


	#
	# parameter string  -- for specific table
	#
	# 	Formats a string suitable for 
	# 		insert into table(fields) values(<paramsString>)...
	# 		where paramString has the form:
	#			'field1','field2',...,'fieldn'
	#
	def paramString(self, table):
		outstring = ''
		for pName in self.params.keys():
			tN = ''
			if pName in self.paramMap.keys():
				tN,fN = self.paramMap[pName].split('.')
			if tN == table:
				if outstring != '':
					outstring += ","
				value = self.params[pName][0]
				outstring = outstring + "\'%s\'" % (value)
		return outstring

	#
	# set string -- for a specific table
	#
	# 	Formats a string suitable for 
	# 	update table set <setstring> where ... 
	# 		<setstring> has the form:
	#			field1="param1",field2="param2"
	def setString(self, table):
		outstring = ''
		for p in self.params.keys():
			if p in self.paramMap.keys():
				tName,fName=self.paramMap[p].split('.')
			else:
				tName = ''
			if tName == table :
				if outstring != '':
					outstring += ','
				outstring += '%s=\"%s\"' % (fName,self.params[p][0])
		return outstring

	def runQuery(self,vmsg,query):
		
		if self.flags['verbose'][0] or self.flags['dryrun'][0]:
			print(vmsg + " query: ", query)

		if self.flags['dryrun'][0] == 0:
			try:
				qval = self.execute(query)
				return qval
			except:
				print("Error in query (%d) [%s]\n" % (qval,vmsg))
				raise SQLerror(query)

	def mergeDBandParameters(self):
		dbkeys=self.dbvalues.keys()
		for fname in self.params.keys():
			if fname in self.paramMap.keys() and \
				self.paramMap[fname] in dbkeys and \
				self.params[fname][0] ==  '' :
					self.params[fname][0] = \
					self.dbvalues[self.paramMap[fname]]

		if self.flags['verbose'][0]:
			print("After Merge of DB-read Values, Parameters are:")
			for p in self.params.keys():
				print("%s = %s" % (p,self.params[p][0]))
		return 0

	# ------------------   END GENERIC Helper Functions ---------------------

