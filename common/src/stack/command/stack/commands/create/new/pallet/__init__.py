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
from collections import UserDict
from random import randrange
import stack
import stack.commands


class Textsub(UserDict):
	"""Substitutes variables in the text with their values
	from the compiled dictionary"""

	def __init__(self, d=None):
		self.re = None
		self.regex = None
		UserDict.__init__(self, d)

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

	<param type='string' name='os'>
	The OS of the pallet. 'sles', 'redhat' are acceptable options.
	Any other values will result in a pallet unrecognized by stacki
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
		d = {"@template@" : self.name,
			"@version@" : self.version,
			"@color@" : self.color,
			"@os@": self.osname,
			"template.xml" : "%s.xml" % self.name,
			"template.spec.in" : "%s.spec.in" % self.name,
			"roll-template-usersguide.spec.in" :
				"roll-%s-usersguide.spec.in" % self.name,
		}

		self.d = Textsub(d)
		self.d.compile()

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

		text = self.d.sub(self.readFile(namein))
		self.writeFile(nameout, text)


	def createDirsFiles(self):
		""" Create directory structure for the new pallet"""
		if os.path.exists('./template'):
			template_dir = './template'
		else:
			template_dir = \
				'/opt/stack/share/build/src/pallet/template'

		shutil.copytree(template_dir, self.name)
		for (r, d, f) in os.walk(self.name):
			for directory in d:
				if 'template' in directory:
					newdir = directory.replace('template', self.name)
					os.rename(os.path.join(r, directory),
						os.path.join(r, newdir))

		for (r, d, f) in os.walk(self.name):
			for filename in f:
				if 'template' in filename:
					fn = os.path.join(r, filename.replace('template', self.name))
					os.rename(os.path.join(r, filename), fn)
				else:
					fn = os.path.join(r, filename)
				self.update(fn, fn)

	def run(self, params, args):

		(self.name, self.version, self.color, self.osname) = self.fillParams([
			('name', None, True),
			('version', '1.0'),
			('color', self.colorNode()),
			('os', 'sles'),
			])

		self.setDict()
		self.createDirsFiles()
