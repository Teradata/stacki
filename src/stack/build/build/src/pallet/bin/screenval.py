#!/opt/stack/usr/bin//python
#
# Helper script, is used by roll/bin/make-screen-val.py
# Is not used directly by the users. 
#
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
#

from __future__ import print_function
import os
import sys
import string
import stack.gen
import stack.file
import stack.gen
import stack.app
from xml.dom                 import ext
from xml.dom.ext.reader.Sax2 import FromXmlStream
from xml.sax._exceptions     import SAXParseException
from stack.util import KickstartError


class ScreenNodeFilter(stack.gen.NodeFilter):
	def acceptNode(self, node):
		if node.nodeName == 'kickstart':
			return self.FILTER_ACCEPT
			
		if not self.isCorrectArch(node):
			return self.FILTER_SKIP

		if node.nodeName in [ 
			'screen',
			'title',
			'variable',
			'code',
			]:
			return self.FILTER_ACCEPT
		else:
			return self.FILTER_SKIP


class Generator(stack.gen.Generator):

	def __init__(self):
		stack.gen.Generator.__init__(self)	

		self.screens = []
		self.out = "";

	
	##
	## Parsing Section
	##
	
	def parse(self, file):
		doc  = FromXmlStream(file)

		filter = ScreenNodeFilter(self.getArch())
		iter = doc.createTreeWalker(doc, filter.SHOW_ELEMENT,
			filter, 0)
		node = iter.nextNode()

		while node:
			if node.nodeName == 'screen':
				self.screens.append({})
				child = iter.firstChild()
				while child:
					self.handle_screenChild(child)
					child = iter.nextSibling()
			node = iter.nextNode()
			
	# <screen>
	
	def handle_screenChild(self, node):
		try:
			eval('self.handle_screen_%s(node)' % node.nodeName)
		except:
			pass

	# <screen>
	#	<title>
	# </screen>
	def handle_screen_title(self, node):
		self.screens[-1]['title'] = '%s' % (self.getChildText(node))
		return


	# <screen>
	#	<variable>
	# </screen>
	def handle_variableChild(self, node):
		try:
			eval('self.handle_variable_%s(node)' % node.nodeName)
		except:
			pass
		return


	def handle_screen_variable(self, node):
		if not self.screens[-1].has_key('variables'):
			self.screens[-1]['variables'] = [{}]
		else:
			self.screens[-1]['variables'].append({})

		for child in node.childNodes:
			self.handle_variableChild(child)

		return


	# <screen>
	#	<variable>
	#		<label>
	# </screen>
	def handle_variable_label(self, node):
		self.screens[-1]['variables'][-1]['label'] = \
			'%s' % (self.getChildText(node))
		return

	# <screen>
	#	<variable>
	#		<name>
	# </screen>
	def handle_variable_name(self, node):
		self.screens[-1]['variables'][-1]['name'] = \
			'%s' % (self.getChildText(node))
		return

	# <screen>
	#	<variable>
	#		<type>
	# </screen>
	def handle_variable_type(self, node):
		self.screens[-1]['variables'][-1]['type'] = \
			'%s' % (self.getChildText(node))
		return

	# <screen>
	#	<variable>
	#		<size>
	# </screen>
	def handle_variable_size(self, node):
		self.screens[-1]['variables'][-1]['size'] = \
			'%s' % (self.getChildText(node))
		return

	# <screen>
	#	<variable>
	#		<default>
	# </screen>
	def handle_variable_default(self, node):
		self.screens[-1]['variables'][-1]['default'] = \
			'%s' % (self.getChildText(node))
		return

	# <screen>
	#	<variable>
	#		<value>
	# </screen>
	def handle_variable_value(self, node):
		self.screens[-1]['variables'][-1]['value'] = \
			'%s' % (self.getChildText(node))
		return

	# <screen>
	#	<variable>
	#		<validate>
	# </screen>
	def handle_variable_validate(self, node):
		self.screens[-1]['variables'][-1]['validate'] = \
			'%s' % (self.getChildText(node))
		return

	# <screen>
	#	<variable>
	#		<help>
	# </screen>
	def handle_variable_help(self, node):
		self.screens[-1]['variables'][-1]['help'] = \
			'%s' % (self.getChildText(node))
		return

	# <screen>
	#	<variable>
	#		<option>
	# </screen>
	def handle_variable_option(self, node):
		if not self.screens[-1]['variables'][-1].has_key('option'):
			self.screens[-1]['variables'][-1]['option'] = []

		self.screens[-1]['variables'][-1]['option'].append(
			'%s' % (self.getChildText(node)))
		return

	# <screen>
	#	<code>
	# </screen>
	def handle_screen_code(self, node):
		if not self.screens[-1].has_key('code'):
			self.screens[-1]['code'] = ''

		self.screens[-1]['code'] += '%s' % (self.getChildText(node))
		return

	# <screen>
	#	<code>
	#		<include>
	# </screen>
	def handle_screen_include(self, node):
		self.screens[-1]['code'] = '%s' % (self.getChildText(node))
		return

	# <*>
	#	<*> - tags that can go inside any other tags
	# </*>
	def getChildText(self, node):
		text = ''
		for child in node.childNodes:
			if child.nodeType == child.TEXT_NODE:
				text += child.nodeValue
			elif child.nodeType == child.ELEMENT_NODE:
				text += eval('self.handle_screen_%s(child)' \
					% (child.nodeName))
		return text

	
	##
	## Generator Section
	##
	def generateScreen(self, screen, i):
		if self.screens[i].has_key('code'):
			print(self.screens[i]['code'])
			print("")

		print("function screen%d()" % (i))
		print("{")

		print("\tvar\td_title = " + \
			"top.workarea.document.createElement('div');")
		print("\tvar\td_vars = " + \
			"top.workarea.document.createElement('div');")
		print("\tvar\td_help = " + \
			"top.help.document.createElement('div');")
		print("\tvar\td_buttons = " + \
			"top.workarea.document.createElement('div');")
		print("\tvar\thelptext;")

		print("")

		#
		# output the screen title
		#
		print("\td_title.id = 'screen-title';")
		print("\td_title.appendChild(top.addTitleText" + \
			"('%s'));" % (self.screens[i]['title']))
		print("\ttop.screen_title[%d] = d_title;" % (i))

		print("")

		#
		# output the screen variables
		#
		print("\td_vars.id = 'screen-variables';")
		for variable in self.screens[i]['variables']:
			if not variable.has_key('type'):
				inputtype = 'text'
			else:
				if variable['type'] == 'password':
					inputtype = 'password'
				elif variable['type'] == 'hidden':
					inputtype = 'hidden'
				elif variable['type'] == 'radio':
					inputtype = 'radio'
				elif variable['type'] == 'menu':
					inputtype = 'menu'
				else:
					inputtype = 'text'

			if not variable.has_key('size'):
				size = 20
			else:
				size = variable['size']

			if variable.has_key('value') \
						and variable['value'] != '':
				value = variable['value']
			elif variable.has_key('default'):
				value = variable['default']
			else:
				value = ''

			if not variable.has_key('validate'):
				validate = 'null'
			else:
				validate = 'top.screens.%s' % \
					(variable['validate'])

			if inputtype == 'menu':
				print("\tvar options = new Array();")
				if variable.has_key('option'):
					j = 0
					for option in variable['option']:
						o = "\toptions[%d] = " % (j)
						o += "'%s';" % (option)
						print(o)
						j = j +1

				print("\td_vars.appendChild(top.addToMenu(" + \
					"'%s'" % (variable['label']) + \
					", '%s'" % (variable['name']) + \
					", '%s'" % (size) + \
					", %s" % (validate) + \
					", options" + \
					", '%s'));" % (value))
			else:
				print("\td_vars.appendChild(top.addToForm(" + \
					"'%s'" % (inputtype) + \
					", '%s'" % (variable['label']) + \
					", '%s'" % (variable['name']) + \
					", '%s'" % (size) + \
					", '%s'" % (value) + \
					", %s));" % (validate))
		print("\ttop.screen_variables[%d] = d_vars;" % (i))

		print("")

		#
		# output the screen help
		#
		print("\td_help.id = 'screen-help';")
		for variable in self.screens[i]['variables']:
			if not variable.has_key('help'):
				continue
			else:
				help = variable['help']

			print("\td_help.appendChild(top.addToHelp(" + \
				"'%s:'" % (variable['label']) + \
				", '%s'));" % (help))
		print("\ttop.screen_help[%s] = d_help;" % (i))

		#
		# output the screen buttons
		#
		print("")
		print("\td_buttons.id = 'screen-buttons';")
		print("\td_buttons.appendChild(" + \
			"top.addButton('Back', top.prevScreen));")
		print("\td_buttons.appendChild(" + \
			"top.addButton('Validate', " + \
				"validate_screen%d));" % (i))
		print("\ttop.screen_buttons[%s] = d_buttons;" % (i))

		#
		# end the 'function screen[0-9]*' function
		#
		print("}")

		#
		# now output the form validation code. this is just a
		# concatenation of all the variable validators
		#
		validatefunctions = []
		for variable in self.screens[i]['variables']:
			if variable.has_key('validate'):
				functioncall = variable['validate'] + '(e)'
				validatefunctions.append(functioncall)

		#
		# register the screen form validation function with
		# the parent screen
		#
		if validatefunctions == []:
			validatefunctions = [ 'true' ]

		#
		# now print out the screen validation code
		#
		print("")
		print("function validate_screen%d(e)" % (i))
		print("{")
		print("\tvar retval = true;")
		print("")
		print("\tif ((" + \
			string.join(validatefunctions, ' && ') + ")) {")
		print("\t\ttop.savevalues();")
		print("\t\ttop.nextScreen();")
		print("\t} else {")
		print("\t\tretval = false;")
		print("\t}")
		print("")
		print("\treturn(retval);")
		print("}")
		print("")

		return

	def generateValidation(self):
		print("function validate_rollScreen()")
		print("{")
		print("\tvar retval = true;\n")
		print("\t/*")
		print("\t * get all input data ")
		print("\t */")
		print("\tvar ent = top.screen_variables[0];")
		print("\tvar divElements = ent.getElementsByTagName(\"input\");\n")
		print("\tfor (var i = 0; i < divElements.length; i++) {")
		print("\t\tvar elem = divElements[i];")
		print("\t\tif (elem.type == \'hidden\')")
		print("\t\t\t{continue;}")
		print("\t\tif (elem.onclick == undefined && elem.onblur == underfined)")
		print("\t\t\t{continue};")
		print("\t\t/*")
		print("\t\t * call this input validation function")
		print("\t\t */")
		print("\t\telem.validate;")
		print("\t}\n")
		print("\treturn(retval);")
		print("}\n")

		#self.out += txt

		#file = open('val', 'w')
		#file.write(self.out)
		#file.close()

		return

	def printJStext(self, txt):
		print(txt)

	def generate(self, txt):
		print('<html>')
		print('<head>')

		print('<script language="JavaScript">')

		i = 0;
		for screen in self.screens:
			self.generateScreen(screen, i)
			i = i + 1

		print('')
		self.printJStext(txt)

		print('function initScreens()')
		print('{')
		i = 0;
		for screen in self.screens:
			#
			# call the screen functions to initialize them
			#
			print('\tself.screen%d();' % (i))
			i = i + 1
		print('}')

		print('</script>')
		print('</head>')
		print('</html>')

		return


class App(stack.app.Application):

	def __init__(self, argv):
		stack.app.Application.__init__(self, argv)
		self.usage_command 	= os.path.basename(argv[0])
		self.usage_name		= 'Installation Screen Validator'
		self.usage_version	= '1.0'
		self.version		= '1'
		self.sections		= []
		self.generator		= Generator()		

		self.jsdir = None
		self.jstext = ""

		self.htmlFile = 'screens.html'
		sys.stdout = open(self.htmlFile, 'w')
	
		self.getopt.s.extend([('j:', 'javascriptDir')])
		self.getopt.l.extend([('jdir=', 'javascriptDir')])

	def help(self):
		self.usage()
		sys.exit(0)

	
	def usage(self):
		txt = ""
		txt += "\n%s - version %s\n" % (self.usage_name, self.usage_version)
		txt += "Usage: %s [-h] [--help] [-j dir] xmlfile\n" % (self.usage_command)
		txt += "\tOptions in [] can be omitted. The following ooptions are supported:\n"
		txt += "\t-h | --help          prints self usage \n"
		txt += "\t-j dir | --jdir=dir  set javascript directory to dir\n"
		txt += "\txmlfile              path to screen xml file\n"
		txt += "\n"
		sys.stderr.write (txt)

		return

	def usageTail(self):
		return ' [file]'

	def getJStext(self, file):
		f = open(file, 'r')
		lines = f.readlines()
		f.close()
		text = string.join(lines, "")
		self.jstext += text
		self.jstext += "\n"


	def getJSfiles(self):
		listing = os.listdir(self.jsdir)
		for i in listing:
			if i[-2:] != "js":
				continue
			file = os.path.join(self.jsdir, i)
			if not os.path.isfile(file):
				continue
			self.getJStext(file)

		return

	def setJSdir(self, dir):
		# ser javascript directory
		if dir == "default":
			path = os.getcwd() + "/../include/javascript"
		else:
			path = dir

		if os.path.isdir(path):
			self.jsdir = path
		else:
			sys.stderr.write("Directory %s does not exist\n" % (path))
			self.help()            

		return

	def parseArg(self, c):
		if stack.app.Application.parseArg(self, c):
			return 1
		elif c[0] in ('-h', '--help'):
			self.help()
		elif c[0] in ('-j', '--jdir'):
			self.setJSdir(c[1])
		else:
			return 0
		return 1


	def run(self):
		if self.args:
			file = self.args[0]
		else:
			file = sys.stdin
		
		if self.jsdir is None:
			self.setJSdir("default")

		self.getJSfiles()
		self.generator.parse(file)
		self.generator.generate(self.jstext)

		return

		
app = App(sys.argv)
app.parseArgs()
app.run()

