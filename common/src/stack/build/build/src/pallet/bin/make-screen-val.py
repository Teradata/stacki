#! /opt/stack/usr/bin/python
#
# Creates a directory structure <rollname>/screenval for testing roll's screens 
# Prerequisites: 
#    1. uses files from rolls/base/src/screens.
#    2. uses roll/bin/screenval.py 
#
# $Id$
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.2  2010/09/07 23:53:05  bruno
# star power for gb
#
# Revision 1.1  2010/06/22 21:07:44  mjk
# build env moving into base roll
#
# Revision 1.3  2009/05/01 19:07:10  mjk
# chimi con queso
#
# Revision 1.2  2008/10/18 00:56:03  mjk
# copyright 5.1
#
# Revision 1.1  2008/05/15 18:09:53  nadya
# Initial revision. Screens debugging.
#

from __future__ import print_function
import sys
import os
import stack.app
import UserDict
import re
from string import join, find
import shutil


class Textsub(UserDict.UserDict):
	"""Substitutes variables in the text with their values
	from the compiled dictionary"""

	def __init__(self, dict=None):
		self.re = None
		self.regex = None
		UserDict.UserDict.__init__(self, dict)
		return


	def compile(self):
		if len(self.data) > 0:
			if self.re == None:
				self.regex = re.compile("(%s)"  \
					 % join(map(re.escape, self.data.keys()),"|"))
		return

	def __call__(self, match):
		return self.data[match.string[match.start():match.end()]]


	def sub(self, s):
		if len(self.data) == 0:
			return s
		return self.regex.sub(self, s)



class App(stack.app.Application):
	"""Creates a directory structure for a new roll with the 
	required files templates."""

	def __init__(self, argv):
		stack.app.Application.__init__(self, argv)
		self.usage_name = "Create screen verification structure in the  roll directory"
		self.usage_version = "1.0"
		self.version = "1"

		self.setDefaultOpts()
		return

	def usageTail(self):
		return  ' roll'

	def setDirNames(self):
		if len(self.args) != 1:
			self.help()

		base = os.path.dirname(os.path.realpath(sys.argv[0]))[:-3]

		self.roll = base + self.args[0]
		if not os.path.isdir(self.roll):
			print("Error: roll directory %s does not exist" % (self.roll))
			sys.exit(-1)

		self.baseRollDir = base + "base/src/screens/"
		if not os.path.isdir(self.baseRollDir):
			print("Error: roll directory %s does not exist" % (self.baseRollDir))
			sys.exit(-1)
		return


	def setDict(self):
		"""Initialize dictionary """
		# strings to sub in html files
		dict = {"(screen.availWidth, screen.availHeight)": "(900,800)",
				"moveTo(0,0)": "moveTo(500,0)",
				"action=\"/tmp/updates/opt/stack/screens/stack-form.cgi\"":"action=\"\""
		}

		self.dict = Textsub(dict)
		self.dict.compile()
		return


	def setDefaultOpts(self):
		"""Extend command line options"""
		self.getopt.s = ['h']
		self.getopt.l = ['help']
		self.getopt.s.extend([('x:', 'screen')])
		self.getopt.l.extend([('xml=', 'screen')])
		return


	def help(self):
		"""Print usage and exit"""
		self.usage()
		print("\tscreen - XML screen file")
		print("\troll - roll name")
		sys.exit(0)


	def parseArg(self, c):
		"""Parse the command line arguments"""

		if stack.app.Application.parseArg(self,c):
			return 1
		elif c[0] in ('-h', '--help'):
			self.help()
		elif c[0] in ('-x', '--xml'):
			self.xmlname = c[1]
		else:
			return 0
		return 1


	def setScreenXmlFile(self):
		self.screen = os.path.join(self.roll, "nodes", self.xmlname)
		if not os.path.isfile(self.screen):
			print("Error: File %s does not exist" % self.screen)
			sys.exit(-1)
		return


	def update(self, namein, nameout):
		"""Read file, make substitution in the text
		and write it back"""
		text = self.dict.sub(self.readFile(namein))
		self.writeFile(nameout, text)
		return


	def readFile(self, name):
		"""Read text file, return a string"""
		try:
			f = open(name, 'r')
			lines = f.readlines()
			f.close()
		except IOError:
			return None

		return join(lines, "")


	def writeFile(self, name, text):
		"""write text as file"""
		try:
			f = open(name, 'w')
			f.write (text)
			f.close()
		except IOError:
			print("Error writing file %s" % name)


	def createValDir(self):
		""" Create directory structure for the screen validatinon """
		self.setDirNames()
		self.setScreenXmlFile()

		self.rollValDir 	 = self.roll + "/screenval"
		cmd = 'mkdir -p %s' % (self.rollValDir)
		os.system(cmd)

		self.createValDirFiles()
		return


	def createValDirFiles(self):
		Files = ['common.css', 'palette-blue.css',
				'bg-blue.png', 'logo-nourl.png', 'watermark.png',
				'header.html', 'help.html', 'hidden.html', 'status.html', 'workarea.html'
				]

		modFiles = ['stack.html', 'hidden.html',  'workarea.html']

		# copy files as is
		for i in Files:
			src = os.path.join(self.baseRollDir, i)
			dest = os.path.join(self.rollValDir, i)
			shutil.copyfile(src, dest)

		# sub a few strings 
		for i in modFiles:
			src = os.path.join(self.baseRollDir, i)
			dest = os.path.join(self.rollValDir, i)
			self.update(src, dest)

		self.createScreenFile()

		return

	def createScreenFile(self):
		# FIXME - need to put screenval.py somewehre else
		base = os.path.dirname(os.path.realpath(sys.argv[0]))
		cmd =  '%s/screenval.py ' % base
		cmd += '-j %s/include/javascript %s' % (self.roll, self.screen)

		pwd = os.getcwd()
		os.chdir(self.rollValDir)
		os.system(cmd)
		os.chdir(pwd)

		return


	def run(self):
		self.setDict()
		self.createValDir()
	

app=App(sys.argv)
app.parseArgs()
app.run()

