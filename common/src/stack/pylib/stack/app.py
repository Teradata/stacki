#! /opt/stack/bin/python
# 
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@

from __future__ import print_function
import os
import sys
import string
import getopt
import types
import stack.util
import xml
from xml.sax import saxutils
from xml.sax import handler
from xml.sax import make_parser
from xml.sax._exceptions import SAXParseException

class Application:

	def __init__(self, argv=None):

		# Applets (code in the kickstart graph) doesn't pass sys.argv
		# so pick it up anyway to keep everything working.
	
		if not argv:
			argv = sys.argv
	    
		self.args		= []
		self.caller_args	= argv[1:]
		self.usage_command	= os.path.basename(argv[0])
		self.usage_name		= 'Application'
		self.usage_version	= 0

		self.projectName	 = 'stack'
		self.projectVersionName	 = 'base'
		self.projectVersionMajor = '0'
		self.projectVersionMinor = '0'
		self.projectVersionMicro = '0'
	

		self.getopt		= stack.util.Struct()
		self.getopt.s		= [ 'h' ]
		self.getopt.l		= [ 'help' ]

		# Unset our locale
		try:
			del os.environ['LANG']
		except KeyError:
			pass

	
	def run(self):
		sys.exit(-1)

	def projectInfo(self):
		return [ self.projectName,
			 self.projectVersionName,
			 int(self.projectVersionMajor),
			 int(self.projectVersionMinor),
			 int(self.projectVersionMicro) ]

	def getArgs(self):
		return self.args

	def setArgs(self, list):
		self.args = list


	def parseArgs(self, rcbase=None):
		"""Parses the command line arguments and all the relevant
		resource-control (RC) files for this application. The usage_command
		(generally argv[0]) will determine which the name of our rcfile,
		unless overrided with the rcbase argument."""

		# Save any existing options
		args = self.getArgs()

		# First pass to get rcfiles specified on the cmd line
		self.setArgs(self.caller_args)
		self.parseCommandLine()


	def parseCommandLine(self, rcfile=0):
		"""Calls getopt to parse the command line flags. In
		rcfile mode we just get --rcfile options."""

		short = ''
		for e in self.getopt.s:
			if type(e) == type(()):
				short = short + e[0]
			else:
				short = short + e

		long = []
		for e in self.getopt.l:
			if type(e) == type(()):
				long.append(e[0])
			else:
				long.append(e)

		try:
			opts, args = getopt.getopt(self.args, short, long)
		except getopt.GetoptError as msg:
			sys.stderr.write("error - %s\n" % msg)
			self.usage()
			sys.exit(1)

		for c in opts:
			self.parseArg(c)

		if not rcfile:
			self.args = args


	def parseArg(self, c):
		if c[0] in ('-h', '--help'):
			self.help()
			sys.exit(0)
		else:
			return 0
		return 1
    
	def usage(self):

		if 'COLUMNS' in os.environ:
			cols = os.environ['COLUMNS']
		else:
			cols = 80

		list = [ 'Usage: ', self.usage_command, ' ' ]
	
		# Build string of argument-free short options.
		s = '[-'
		for e in self.getopt.s:
			if len(e) == 1:
				s = s + e
		s = s + ']'
		if len(s) == 3:
			s = ''
		list.append(s)

		# Add the argument short options to the above string
		for e in self.getopt.s:
			if type(e) == type(()):
				v = e[0]
				h = e[1]
			else:
				v = e
				h = 'arg'
			if len(v) != 1:
				list.append(' [-' + v[:-1] + ' ' + h + ']')

		# Add argument-free long options
		for e in self.getopt.l:
			if type(e) == type(()):
				v = e[0]
			else:
				v = e
			if v[len(v)-1] != '=':
				list.append(' [--' + v + ']')

		# Add argument long options
		for e in self.getopt.l:
			if type(e) == type(()):
				v = e[0]
				h = e[1]
			else:
				v = e
				h = 'arg'
			if v[len(v)-1] == '=':
				list.append(' [--' + v[:-1] + ' ' + h + ']')

		list.append(self.usageTail())

		# Print the usage, word wrapped to the correct screen size.
		print(self.usage_name, '- version', self.usage_version)
		l = 0
		s = ''
		for e in list:
			if l + len(e) <= cols:
				s = s + e
				l = l + len(e)
			else:
				print(s)
				l = len(e)
				s = e
			if s:
				print(s)


	def help(self):
		self.usage()


	def usageTail(self):
		return ''


	def getArch(self):
		return stack.util.getNativeArch()



