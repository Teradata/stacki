#! /opt/stack/bin/python
#
# Queries a set of binary files for their dynamically-linked libraries.
# Outputs a list of library files (that exist locally), suitable for building
# an RPM package. Uses ldd.
#
# Use 'find -type f -perm -555' to find binaries in a dir.
#
# $Log$
# Revision 1.1  2010/06/22 21:07:44  mjk
# build env moving into base roll
#
# Revision 1.3  2006/01/16 06:49:02  mjk
# fix python path for source built foundation python
#
# Revision 1.2  2003/12/16 21:00:47  fds
# Handles deep dependancies.
#
# Revision 1.1  2003/12/16 20:02:03  fds
# Added support for making i386 compat libs per roll.
#
#

from __future__ import print_function
import sys
import os
import commands
import stack.app

class App(stack.app.Application):
	"""Finds the libraries associated with binaries. Used to 
	make compat-libs rpms for Opteron machines."""

	def __init__(self, argv):
		stack.app.Application.__init__(self, argv)
		self.usage_name = "Compatibility Library Finder"
		self.usage_version = "3.1.0"

	def usageTail(self):
		return """ <list of binary files>"""

	def run(self):
		files = self.getArgs()
		if not files:
			raise ValueError, "I need some input files"

		libs = self.analyze(files)
		while 1:
			extralibs = self.analyze(libs)
			if not extralibs:
				break
			else:
				# Are these truly new?
				size = len(libs)
				for l in extralibs.keys():
					libs[l]=1
				if len(libs) <= size:
					break

		for lib in libs.keys():
			print(lib)
	

	def analyze(self, files):
		"""Finds the library dependancies for a set of executables.
		Called multiple times to catch deep deps."""

		libs = {}
		for f in files:
			rc, out = commands.getstatusoutput("/usr/bin/ldd %s" % f)
			if rc!=0:
				continue
			#print f, out
			lines = out.split('\n')
			for line in lines:
				fields = line.split(" => ")
				if len(fields) != 2:
					continue
				lib = fields[1]
				linklib = lib.split()[0]
				# A heuristic to help with a hard problem..
				for loc in ('/lib','/usr/lib'):
					if linklib.find(loc) == 0:
						abslib = linklib
						try:
							abslib = os.path.join(
								os.path.dirname(linklib), 
								os.readlink(linklib))
						except OSError:
							pass
						libs[abslib] = 1
		return libs



app=App(sys.argv)
app.parseArgs()
app.run()


