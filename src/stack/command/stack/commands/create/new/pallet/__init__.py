# $Id: __init__.py,v 1.3 2011/02/03 23:01:22 bruno Exp $
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
# Revision 1.3  2011/02/03 23:01:22  bruno
# fix help for command
#
# Revision 1.2  2010/09/07 23:52:51  bruno
# star power for gb
#
# Revision 1.1  2009/06/08 22:24:51  bruno
# create the directory structure in order to build a new roll from scratch
#
#

import re
import os
import shutil
import string
import UserDict
from random import randrange
import stack
import stack.commands

class Textsub(UserDict.UserDict):
	"""Substitutes variables in the text with their values
	from the compiled dictionary"""

	def __init__(self, dict=None):
		self.re = None
		self.regex = None
		UserDict.UserDict.__init__(self, dict)

	def compile(self):
		if len(self.data) > 0:
			if self.re == None:
				self.regex = re.compile("(%s)" % \
					'|'.join(map(re.escape,
						self.data.keys())))

	def __call__(self, match):
		return self.data[match.string[match.start():match.end()]]

	def sub(self, s):
		if len(self.data) == 0:
			return s
		return self.regex.sub(self, s)


class Command(stack.commands.create.new.command):
	"""	
	Create a new pallet from a template.

	<arg type='string' name='version'>	
	</arg>

	<arg type='string' name='name'>	
	</arg>

	<arg type='string' name='color'>	
	</arg>
	
	<param type='string' name='name'>
	</param>
	
	<param type='string' name='version'>
	</param>

	<param type='string' name='color'>
	</param>

	<example cmd='create new pallet'>
	</example>
	"""


	def colorNode(self):
		"""Randomly pick a color for the new pallet. only do this if
		no color is provided on the command line"""

		colors = [
			"aliceblue", "antiquewhite", "aquamarine", "azure",
			"beige", "bisque", "blanchedalmond", "blueviolet",
			"brown", "burlywood", "cadetblue", "chartreuse", 
			"chocolate", "coral", "cornflowerblue", "cornsilk",
			"crimson", "cyan", "darkblue", "darkcyan", 
			"darkgoldenrod", "darkgray", "darkgreen", "darkkhaki",
			"darkmagenta", "darkolivegreen", "darkorange",
			"darkorchid", "darkred", "darksalmon", "darkseagreen",
			"darkslateblue", "darkslategray", "darkturquoise",
			"darkviolet", "deeppink", "deepskyblue", "dimgray",
			"dodgerblue", "firebrick", "floralwhite",
			"forestgreen", "gainsboro", "ghostwhite",
			"gold", "goldenrod", "greenyellow", "honeydew",
			"hotpink", "indianred", "indigo", "ivory",
			"khaki", "lavender", "lavenderblush", "lawngreen",
			"lemonchiffon", "lightblue", "lightcoral", "lightcyan",
			"lightgoldenrodyellow", "lightgreen", "lightgrey",
			"lightpink", "lightsalmon", "lightseagreen",
			"lightskyblue", "lightslategray", "lightsteelblue",
			"lightyellow", "limegreen", "linen", "magenta",
			"mediumaquamarine", "mediumblue", "mediumorchid",
			"mediumpurple", "mediumseagreen", "mediumslateblue",
			"mediumspringgreen", "mediumturquoise",
			"mediumvioletred", "midnightblue", "mintcream",
			"mistyrose", "moccasin", "navajowhite", "oldlace",
			"olivedrab", "orange", "orangered", "orchid",
			"palegoldenrod", "palegreen", "paleturquoise",
			"palevioletred", "papayawhip", "peachpuff", "peru",
			"pink", "plum", "powderblue", "rosybrown", "royalblue",
			"saddlebrown", "salmon", "sandybrown", "seagreen",
			"seashell", "sienna", "skyblue", "slateblue",
			"slategray", "snow", "springgreen", "steelblue",
			"tan", "thistle", "tomato", "turquoise",
			"violet", "wheat", "whitesmoke", "yellowgreen"
			]

		return colors[randrange(0, len(colors))]


	def setDict(self):
		"""Initialize dictionary. Key - a variable to
		be substituted, value - the substitution value"""
		dict = {"@template@" : self.name,
			"@version@" : self.version,
			"@color@" : self.color,
			"template.xml" : "%s.xml" % self.name,
			"template.spec.in" : "%s.spec.in" % self.name,
			"roll-template-usersguide.spec.in" :
				"roll-%s-usersguide.spec.in" % self.name,
		}

		self.dict = Textsub(dict)
		self.dict.compile()


	def changeName(self, dir, name):
		"""If a name contains 'template', substitute with the pallet
		name"""

		str = "template"
		i = string.find(name, str) 
		if i == -1 :
			return name

		new =  name[0:i] + self.name + name[i+len(str):]
		os.rename(name, new)
		return new 


	def readFile(self, name):
		"""Read text file, return a string"""
		try:
			f = open(name, 'r')
			lines = f.readlines()
			f.close()
		except IOError:
			return None

		return ''.join(lines)


	def writeFile(self, name, text):
		"""write text as file"""
		try:
			f = open(name, 'w')
			f.write (text)
			f.close()
		except IOError:
			print "Error writing file %s" % name


	def update(self, namein, nameout):
		"""Read file, make substitution in the text
		and write it back"""

		text = self.dict.sub(self.readFile(namein))
		self.writeFile(nameout, text)


	def rollName(self, arg, dirname, fnames):
		"""Rename 'template/' with the pallet name, update file names to
		include a pallet name where needed, and update file text."""
		dirname = self.changeName("", dirname)

		for file in fnames:
			fullname = os.path.join(dirname, file)

			if string.find(fullname, "images/") > 0 :
				# don't change image files names
				continue

			if os.path.isfile(fullname):
				newname = self.changeName("", fullname)
				self.update(newname, newname)

	def createDirsFiles(self):
		""" Create directory structure for the new pallet"""
		if os.path.exists('./template'):
			template_dir = './template'
		else:
			template_dir = \
				'/opt/stack/share/build/src/pallet/template'

		shutil.copytree(template_dir, self.name)

		os.path.walk(self.name, self.rollName, [])


	def run(self, params, args):
		(args, self.name) = self.fillPositionalArgs(('name', ))

		if not self.name:
			self.abort('must supply a name for the new pallet')

		(self.version, self.color) = self.fillParams([
			('version', '1.0'), ('color', self.colorNode()) ])

		self.setDict()
		self.createDirsFiles()

