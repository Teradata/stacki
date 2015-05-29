# $Id$
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
# Revision 1.10  2010/09/07 23:52:56  bruno
# star power for gb
#
# Revision 1.9  2009/05/01 19:06:59  mjk
# chimi con queso
#
# Revision 1.8  2008/10/18 00:55:55  mjk
# copyright 5.1
#
# Revision 1.7  2008/10/16 20:35:20  bruno
# when printing a roll's commands, only process one version of the roll,
# otherwise, every command will be listed multiple times.
#
# Revision 1.6  2008/03/06 23:41:38  mjk
# copyright storm on
#
# Revision 1.5  2007/07/04 01:47:38  mjk
# embrace the anger
#
# Revision 1.4  2007/06/28 20:26:25  bruno
# done with 'rocks list'
#
# Revision 1.3  2007/06/26 05:19:39  phil
# properly use getRollNames
#
# Revision 1.2  2007/06/19 16:42:42  mjk
# - fix add host interface docstring xml
# - update copyright
#
# Revision 1.1  2007/06/16 02:39:51  mjk
# - added list roll commands (used for docbook)
# - docstrings should now be XML
# - added parser for docstring to ASCII or DocBook
# - ditched Phil's Network regex stuff (will come back later)
# - updated several docstrings
#
# Revision 1.4  2007/06/07 21:23:05  mjk
# - command derive from verb.command class
# - default is MustBeRoot
# - list.command / dump.command set MustBeRoot = 0
# - removed plugin non-bugfix
#
# Revision 1.3  2007/06/07 17:21:51  mjk
# - added RollArgumentProcessor
# - added trimOwner option to the endOutput method
# - roll based commands are uniform
#
# Revision 1.2  2007/06/01 17:44:10  bruno
# more than one version of a roll in the rolls database caused redundant
# info to be listed -- the 'distinct' keyword only prints unique values
#
# Revision 1.1  2007/05/31 21:25:55  bruno
# rocks enable/disable/list roll
#
#


import os
import stat
import time
import sys
import string
import stack.file
import stack.commands


class Command(stack.commands.RollArgumentProcessor,
	stack.commands.list.command):
	"""
	List the commands provided by a pallet.
	
	<arg optional='1' type='string' name='pallet' repeat='1'>
	List of pallets. This should be the pallet base names (e.g., base, hpc,
	kernel). If no pallets are listed, then commands for all the pallets
	are listed.
	</arg>
	
	<example cmd='list pallet command stacki'>
	Returns the the list of commands installed by the stacki pallet.
	</example>		
	"""		

	def run(self, params, args):

		tree = stack.file.Tree(stack.commands.__path__[0])
		dirs = tree.getDirs()
		dirs.sort()

		dict = {}		
		for dir in dirs:
			if not dir:
				continue
			modpath = 'stack.commands.%s' % \
				string.join(dir.split(os.sep),'.')
			__import__(modpath)
			module = eval(modpath)
			try:
				o = getattr(module, 'Command')
			except AttributeError:
				continue
			try:
				o = getattr(module, 'RollName')
			except AttributeError:
				continue
			if not dict.has_key(o):
				dict[o] = []
			dict[o].append(string.join(dir.split(os.sep), ' '))

		# If args are mentioned then use them, if not get all
		# pallet names from the database
		if len(args) == 0:
			roll_list = self.getRollNames(args, params)
			f = lambda x: x[0]
			rolls = map(f, roll_list)
		else:
			rolls = args
			
		seenrolls = []

		self.beginOutput()
		for roll in rolls:
			if roll in seenrolls:
				continue
			seenrolls.append(roll)
		
			if dict.has_key(roll):
				for command in dict[roll]:
					self.addOutput(roll, command)
			else:
				if len(rolls) > 1:
					self.addOutput(roll, '')
		self.endOutput(header=['pallet', 'command'])

