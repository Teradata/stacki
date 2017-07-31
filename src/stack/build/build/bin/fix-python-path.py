#!/opt/stack/usr/bin/python
#
# Fixes the top line of a python script to use the foundation
# version.
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.2  2010/09/07 23:53:04  bruno
# star power for gb
#
# Revision 1.1  2010/06/22 21:07:44  mjk
# build env moving into base roll
#
# Revision 1.7  2009/05/01 19:06:45  mjk
# chimi con queso
#
# Revision 1.6  2008/10/18 00:55:43  mjk
# copyright 5.1
#
# Revision 1.5  2008/03/06 23:41:28  mjk
# copyright storm on
#
# Revision 1.4  2007/06/23 04:03:16  mjk
# mars hill copyright
#
# Revision 1.3  2006/09/11 22:46:51  mjk
# monkey face copyright
#
# Revision 1.2  2006/08/10 00:09:12  mjk
# 4.2 copyright
#
# Revision 1.1  2006/01/10 18:04:42  mjk
# *** empty log message ***
#
# Revision 1.1  2006/01/10 18:02:52  mjk
# *** empty log message ***
#

import sys
import os
import string
import stack.app

class App(stack.app.Application):

	def __init__(self, argv):
		stack.app.Application.__init__(self, argv)
		self.usage_name = "Fix Python Path"
		self.usage_version = "1.0"
		self.python = '/opt/stack/usr/bin/python'

	def run(self):
		for file in self.args:
			fin = open(file, 'r')
			lines = fin.readlines()
			if lines[0][0] == '#':
				lines[0] = '#! %s\n' % self.python
			fin.close()

			fout = open(file, 'w')
			fout.write(string.join(lines, ''))
			fout.close()
			

	

app=App(sys.argv)
app.parseArgs()
app.run()

