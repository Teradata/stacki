# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import re
import os
import shutil
import string
from collections import UserDict
from random import randrange
import stack
import stack.commands


class Textsub(UserDict):
	"""Substitutes variables in the text with their values
	from the compiled dictionary"""

	def __init__(self, dict=None):
		self.re = None
		self.regex = None
		UserDict.__init__(self, dict)

	def compile(self):
		if len(self.data) > 0:
			if self.re is None:
				self.regex = re.compile("(%s)" % 
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
	Create a skeleton directory structure for a pallet
	source.

	This command is to be used mainly by pallet developers.

	This command creates a directory structure from
	templates that can be then be populated with required
	software and configuration.

	Refer to Pallet Developer Guide for more information.

	<param type='string' name='name' optional='0'>	
	Name of the new pallet to be created.
	</param>
	
	<param type='string' name='version'>
	Version of the pallet. Typically the version of the
	application to be palletized.
	</param>

	<example cmd='create new pallet name=valgrind version=3.10.1'>
	Creates a new pallet for Valgrind version 3.10.1.
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
		i = name.find(str)
		if i == -1:
			return name
		
		new = name[0:i] + self.name + name[i + len(str):]
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
			f.write(text)
			f.close()
		except IOError:
			print("Error writing file %s" % name)


	def update(self, namein, nameout):
		"""Read file, make substitution in the text
		and write it back"""

		text = self.dict.sub(self.readFile(namein))
		self.writeFile(nameout, text)


	def rollName(self, dirname, dirs, fnames):
		"""Rename 'template/' with the pallet name, update file names to
		include a pallet name where needed, and update file text."""
		dirname = self.changeName("", dirname)
		for file in fnames:
			fullname = os.path.join(dirname, file)
			if fullname.find("images/") > 0:
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
		for root,dirs,fnames in os.walk(self.name,self.rollName,[]):
			self.rollName(root,dirs,fnames)


	def run(self, params, args):

		(self.name, self.version, self.color) = self.fillParams([
			('name', None, True),
			('version', '1.0'),
			('color', self.colorNode())
			])
		self.setDict()
		self.createDirsFiles()
