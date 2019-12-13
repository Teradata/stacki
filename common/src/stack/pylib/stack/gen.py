#! /opt/stack/bin/python
# 
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@


import ast
import collections
import os
from xml.sax import handler
import xml.dom.minidom
from stack.bool import str2bool
import stack.cond


class ProfileSnippet:
	
	def __init__(self, text, source):
		self.source = source
		self.text   = text

	def getText(self):
		return self.text

	def getSource(self):
		return self.source


class ProfileSection:

	def __init__(self):
		self.snippets = []

	def append(self, text, source=None):
		self.snippets.append(ProfileSnippet(text, source))
		return self

	def generate(self, cdata=True):
		prev = None
		open = False
		list = []

		if cdata:
			cdataStart = '<![CDATA['
			cdataEnd   = ']]>'
		else:
			cdataStart = ''
			cdataEnd   = ''

		for snippet in self.snippets:
			source = snippet.getSource()
			text   = snippet.getText()

			if not source:
				source = 'internal'

			if source != prev:
				if open:
					list.append('\t%s</section>' % cdataEnd)
				list.append('\t<section source="%s">%s' % 
					    (source, cdataStart))
				open = True
			list.append(text)
			prev = source
		if open:
			list.append('\t%s</section>' % cdataEnd)
		return list


class PackageSet:

	def __init__(self):
		self.packages = {}

	def append(self, package, enabled=True, source=None):
		"""
		Add a package to the set, Once a package is disabled it stays
		disabled, so only update the dictionary if the package
		doesn't exist or is currently enabled.
		"""
		if package in self.packages:
			(e, n) = self.packages[package]
			if e:
				self.packages[package] = (enabled, source)
		else:
			self.packages[package] = (enabled, source)


	def getPackages(self):

		dict = { 'enabled': {}, 'disabled' : {} }

		for (package, (enabled, source)) in self.packages.items():
			if enabled:
				d = dict['enabled']
			else:
				d = dict['disabled']
			if source not in d:
				d[source] = []
			d[source].append(package)
		
		return dict

		
class ParsingTools:

	def getAttr(self, node, attr, *, consume=False, default=''):
		a = node.attributes.getNamedItem(attr)
		if a:
			if consume:
				node.removeAttribute(attr)
			return a.value
		else:
			return default

	def removeNode(self, node):
		"""Safe way to remove a node, just replace it with empty text. The DOM
		library sometimes gets confused on removing nodes near
		the end of the document.

		"""
		node.parentNode.replaceChild(self.newTextNode(''), node)

	def collect(self, node):
		l = []
		for child in node.childNodes:
			if child.nodeType in [ child.TEXT_NODE, child.CDATA_SECTION_NODE]:
				l.append(child.nodeValue)
			elif child.nodeType == child.ELEMENT_NODE:
				try:
					fn = eval('self.collect_%s_%s' % (child.prefix, 
									  child.localName))
				except AttributeError:
					fn = lambda child: child.toxml()
				l.append(fn(child))

		return ''.join(l)
	

## -----------------------------------------------------------------------------
## Traversors
## -----------------------------------------------------------------------------


class Traversor(ParsingTools):

	def __init__(self, generator):
		self.gen = generator

	def newElementNode(self, qname):
		"""Creates a new tag to be added to the document.

		"""
		(ns, tag) = qname.split(':')
		
		uri = self.getAttr(self.gen.root, 'xmlns:%s' % ns)
		return self.gen.doc.createElementNS(uri, qname)

	def newTextNode(self, msg):
		"""Creates a new text block to be added to the document.

		"""
		return self.gen.doc.createTextNode(msg)

	def setAttribute(self, node, qname, value):
		"""Sets an attribute a tag in the document.

		"""
		(ns, attr) = qname.split(':')

		uri = self.getAttr(self.gen.root, 'xmlns:%s' % ns)
		node.setAttributeNS(uri, qname, value)

	def debug(self, msg, *, level='info'):
		"""Adds a debug message to the document.

		<stack:debug level=level>msg</stack:debug>

		"""
		node = self.newElementNode('stack:debug')
		node.appendChild(self.newTextNode(msg))

		self.setAttribute(node, 'stack:level', level)

		self.gen.root.appendChild(node)



	def pre(self):
		"""Runs before the traversal starts.

		Derived classes can use this to setup the traversal.

		"""
		pass

	def post(self):
		"""Runs after the traversal ends.

		Derived classes can use this the clean up after the
		traversal.

		"""
		pass

	def traverse(self, node):
		"""Default handler for all tags.

		To handle specific tags derived classes must define
		methods of the form traverse_NS_TAG where NS is the
		namespace string and TAG is the tag string ('-' are
		mapped to '_').  All traverse methods should return
		True to continue the traversal and False stop
		decending to child nodes.

		"""
		return True


class SetupTraversor(Traversor):
	"""First Pass

	"""

	def pre(self):
		self.nodeFiles = collections.OrderedDict()
		self.nodeID    = 0

	def traverse_stack_profile(self, node):
		"""<stack:profile>

		Extracts the stack:attrs XML attribute and uses this
		to create the generators attributes. This needs to be
		done before any stack:cond processing can happen.

		"""
		if node.attributes:
			attrs = node.attributes.getNamedItem('stack:attrs')
			if attrs:
				dict = ast.literal_eval(attrs.value)
				for (k, v) in dict.items():
					self.gen.attrs[k] = v
		else:
			self.debug('<stack:profile> missing stack:attrs', 
				   level='error')

		return True

	def traverse(self, node):
		"""<*>

		Adds a unique stack:id to all tags, and records the
		ordering of the original XML node files. Both of these
		are used to debugging.

		"""

		self.nodeID += 1
		node.setAttribute('stack:id', '%d' % self.nodeID)

		nodefile = self.getAttr(node, 'stack:file')
		if nodefile:
			nodefile = os.path.relpath(nodefile, '/export/stack')
			if nodefile not in self.nodeFiles:
				self.nodeFiles[nodefile] = True
				self.debug('parsed %s' % nodefile, level='info')

		return True


class PruningTraversor(Traversor):
	"""Second Pass

	Removes nodes from the document.

	"""

	def traverse_stack_profile(self, node):
		"""<stack:profile>

		"""
		return True

	def traverse(self, node):
		"""<*>

		Evaluates all the stack:cond XML attributes and
		removes all the False nodes in the tree.

		"""

		arch	 = self.getAttr(node, 'stack:arch')
		osname	 = self.getAttr(node, 'stack:os')
		release  = self.getAttr(node, 'stack:release')
		nodefile = self.getAttr(node, 'stack:file')
		nodeid   = self.getAttr(node, 'stack:id')

		if arch:
			self.debug('stack:arch is deprecated (%s)' % nodefile, 
				   level='warning')
		if osname:
			self.debug('stack:os is deprecated (%s)' % nodefile,
				   level='warning')
		if release:
			self.debug('stack:release is deprecated (%s)' % nodefile,
				   level='warning')

		cond = self.getAttr(node, 'stack:cond')
		expr = stack.cond.CreateCondExpr(arch, osname, release, cond)

		if not expr: # no cond keep going
			return True

		passed = stack.cond.EvalCondExpr(expr, self.gen.attrs)

		self.debug('cond is %s in node %s "%s"' % (passed, nodeid, expr))

		if not passed:
			parent = node.parentNode
			if parent: # node might be orphaned
				self.removeNode(node)
			return False # subtree is gone stop

		return True

		
class ExpandingTraversor(Traversor):
	"""Third Pass

	Expands/Replaces nodes

	"""

	def rcsBegin(self, file, owner, perms):
		"""
		If the is the first time we've seen a file ci/co it.  Otherwise
		just track the ownership and perms from the <file> tag .
		"""
		rcsdir	 = os.path.join(os.path.dirname(file), 'RCS')
		rcsfile  = '%s,v' % os.path.join(rcsdir, os.path.basename(file))
		l	 = []


		l.append('')
		if file not in self.rcsFiles:
			l.append('if [ -e /opt/stack/bin/rcs ]; then')
			l.append('\tif [ ! -f %s ]; then' % rcsfile)
			l.append('\t\tif [ ! -f %s ]; then' % file)
			l.append('\t\t\ttouch %s' % file)
			l.append('\t\tfi')
			l.append('\t\tif [ ! -d %s ]; then' % rcsdir)
			l.append('\t\t\tmkdir -m 700 %s' % rcsdir)
			l.append('\t\t\tchown 0:0 %s' % rcsdir)
			l.append('\t\tfi')
			l.append('\t\techo "original" | /opt/stack/bin/ci -q %s' % file)
			l.append('\t\t/opt/stack/bin/rcs -noriginal: %s' % file)
			l.append('\t\t/opt/stack/bin/co -q -f -l %s' % file)
			l.append('\tfi')
			if owner:
				l.append('\tchown %s %s' % (owner, rcsfile))
			l.append('fi')

		# If this is a subsequent file tag and the optional PERMS
		# or OWNER attributes are missing, use the previous value(s).
		
		if file in self.rcsFiles:
			(orig_owner, orig_perms) = self.rcsFiles[file]
			if not perms:
				perms = orig_perms
			if not owner:
				owner = orig_owner

		self.rcsFiles[file] = (owner, perms)
		
		l.append('')

		return '\n'.join(l)

	def rcsEnd(self, file, owner, perms):
		"""
		Run the final ci/co of a <file>.  The ownership of both the
		file and rcs file are changed to match the last requested
		owner in the file tag.	The perms of the file (not the file
		file) are also modified.

		The file is checked out locked, which is why we don't modify
		the perms of the RCS file itself.
		"""
		rcsdir	= os.path.join(os.path.dirname(file), 'RCS')
		rcsfile = '%s,v' % os.path.join(rcsdir, os.path.basename(file))
		l	= []

		l.append('\n')
		l.append('if [ -e /opt/stack/bin/rcs ]; then')
		l.append('\tif [ -f %s ]; then' % file)
		l.append('\t\techo "stack" | /opt/stack/bin/ci -q %s' % file)
		l.append('\t\t/opt/stack/bin/rcs -Nstack: %s' % file)
		l.append('\t\t/opt/stack/bin/co -q -f -l %s' % file)
		l.append('\tfi')

		if owner:
			l.append('\tchown %s %s' % (owner, rcsfile))

		l.append('fi')

		if owner:
			l.append('chown %s %s' % (owner, file))
		if perms:
			l.append('chmod %s %s' % (perms, file))

		l.append('')

		return '\n'.join(l)


	def pre(self):
		self.rcsFiles = { }

	def post(self):
		boot = self.newElementNode('stack:script')
		self.setAttribute(boot, 'stack:stage', 'boot-pre')
		self.setAttribute(boot, 'stack:id', 'rcsEnd')

		for (file, (owner, perms)) in self.rcsFiles.items():
			boot.appendChild(self.newTextNode('%s' % self.rcsEnd(file, owner, perms)))

		self.gen.root.appendChild(boot)


	def traverse_stack_file(self, node):
		"""<stack:file>

		Convert the file tags the shell code along with rcs
		ci/co.

		"""
	
		fileName    = self.getAttr(node, 'stack:name')
		fileMode    = self.getAttr(node, 'stack:mode')
		fileOwner   = self.getAttr(node, 'stack:owner')
		filePerms   = self.getAttr(node, 'stack:perms')
		fileQuoting = self.getAttr(node, 'stack:vars', default='literal')
		fileCommand = self.getAttr(node, 'stack:expr')
		fileText    = self.collect(node)

		fileRCS	    = self.getAttr(node, 'stack:rcs', default='true')
		fileRCS     = str2bool(fileRCS)


		if fileName:
			p, f = os.path.split(fileName)
			s    = 'if [ ! -e %s ]; then mkdir -p %s; fi\n' % (p, p)

			if fileRCS:
				s += self.rcsBegin(fileName, fileOwner, filePerms)

			if fileMode == 'append':
				gt = '>>'
			else:
				gt = '>'

			if fileCommand:
				s += '%s %s %s\n' % (fileCommand, gt, fileName)
			if not fileText:
				s += 'touch %s\n' % fileName
			else:
				if fileQuoting == 'expanded':
					eof = "EOF"
				else:
					eof = "'EOF'"

				s += "cat %s %s << %s" % (gt, fileName, eof)
				if fileText[0] != '\n':
					s += '\n'
				s += fileText
				if fileText[-1] != '\n':
					s += '\n'
				s += 'EOF\n'

			if fileOwner:
				s += 'chown %s %s\n' % (fileOwner, fileName)
			if filePerms:
				s += 'chmod %s %s\n' % (filePerms, fileName)

		node.parentNode.replaceChild(self.newTextNode(s), node)
		return False


class MainTraversor(Traversor):
	"""Main Pass

	"""

	def pre(self):
		self.scripts = { 'install-post': collections.OrderedDict(),
				 'boot-pre'    : collections.OrderedDict(),
				 'boot-post'   : collections.OrderedDict() }

	def shellPackages(self, enabled, disabled):
		pass

	def post(self):
		section  = self.gen.shellSection
		packages = self.gen.packageSet.getPackages()

		enabled = [ ]
		for (nodefile, pkgs) in packages['enabled'].items():
			enabled.extend(pkgs)

		disabled = [ ]
		for (nodefile, pkgs) in packages['disabled'].items():
			disabled.extend(pkgs)

		section.append('''
DO_PACKAGES=1
DO_INSTALL_POST=1
DO_BOOT_PRE=0
DO_BOOT_POST=1

while getopts ":s:" opt; do
	case $opt in
		s)
			DO_PACKAGES=0
			DO_INSTALL_POST=0
			DO_BOOT_PRE=0
			DO_BOOT_POST=0
			case $OPTARG in
				packages)  DO_PACKAGES=1;;
				post)      DO_INSTALL_POST=1;;
				boot-pre)  DO_BOOT_PRE=1;;
				boot-post) DO_BOOT_POST=1;;
				*)         ;;
			esac
			;;
		*)
			;;
	esac
done
''')

		for stage in self.scripts: # write the functions
			for label in self.scripts[stage]:
				section.snippets.append(self.scripts[stage][label])

		#
		# each section must have at least one line in it or else it will
		# throw an error
		#
		script = self.shellPackages(enabled, disabled)
		if script:
			section.append('if [ $DO_PACKAGES -eq 1 ]; then')
			section.append(script)
			section.append('fi\n')

		script = self.scripts['install-post']
		if script:
			section.append('if [ $DO_INSTALL_POST -eq 1 ]; then')
			for label in script:
				section.append('\t%s' % label)
			section.append('fi\n')

		script = self.scripts['boot-pre']
		if script:
			section.append('if [ $DO_BOOT_PRE -eq 1 ]; then')
			for label in script:
				section.append('\t%s' % label)
			section.append('fi\n')

		script = self.scripts['boot-post']
		if script:
			section.append('if [ $DO_BOOT_POST -eq 1 ]; then')
			for label in script:
				section.append('\t%s' % label)
			section.append('fi\n')
		

	def traverse_stack_profile(self, node):
		"""<stack:profile>

		"""
		return True

	def traverse_stack_package(self, node):
		"""<stack:package>

		Build the packageSet.

		"""

		nodefile = self.getAttr(node, 'stack:file')

		meta	 = self.getAttr(node, 'stack:meta', default='false')
		meta     = str2bool(meta)

		enabled  = self.getAttr(node, 'stack:enable', default='true')
		enabled  = str2bool(enabled)

		for line in self.collect(node).split('\n'):
			pkg = line.strip()
			if pkg:
				if meta:
					pkg = '@%s' % pkg
				self.gen.packageSet.append(pkg, enabled, nodefile)

		return False


	def traverse_stack_script(self, node):
		"""<stack:script>

		"""
		stage  = self.getAttr(node, 'stack:stage',  default='install-post')
		chroot = self.getAttr(node, 'stack:chroot', default='true')
		shell  = self.getAttr(node, 'stack:shell')

		if stage in [ 'install-pre', 'install-pre-package' ] or not chroot == 'true':
			return False # ignore pre and nochroot stuff

		l = 'stack_%s_%s' % (stage, self.getAttr(node, 'stack:id'))

		# make sure all the '-' characters are translated to '_' characters
		label = l.translate(str.maketrans('-', '_'))

		fn = [ ]
		code = [ ]
		fn.append('function %s {' % label)
		if shell:
			code.append('cat > /tmp/%s << "__EOF_%s__"' % (label, label))
			code.append('#! %s\n' % shell)
		body = self.collect(node).strip()
		if body:
			code.append(body)
		if shell:
			code.append('__EOF_%s__' % label)
			code.append('chmod +x /tmp/%s' % label)
			code.append('/tmp/%s' % label)
		if not code:
			# the bash shell 'no op' command
			code.append(':')
		fn.extend(code)
		fn.append('}\n\n')

		self.scripts[stage][label] = stack.gen.ProfileSnippet('\n'.join(fn),
								      self.getAttr(node, 'stack:file'))
		return False

	def traverse_stack_stacki(self, node):
		"""<stack:stacki>

		Records the stacki section and removes it from the
		document.

		"""
		self.gen.stackiSection.append(self.collect(node),
					      self.getAttr(node, 'stack:file'))
		self.removeNode(node)
		return False

	# <stack:debug>
	
	def traverse_stack_debug(self, node):
		"""<stack:debug>

		Records the debug messages

		"""
		nodefile = self.getAttr(node, 'stack:file')
		level    = self.getAttr(node, 'stack:level')
		msg      = self.collect(node)

		self.gen.debugSection.append('%-6s- %s' % (level, msg), nodefile)
		self.removeNode(node)
		return False

	# <*>

	def traverse(self, node):
		"""<*>

		Warns about unhandled tags.

		"""

		attrs = []
		for (key, val) in node.attributes.items():
			if key == 'stack:file': # omit from msg
				continue
			attrs.append('%s="%s"' % (key, val))
		
		msg = '%-6s- <%s' % ('error', node.tagName)
		if attrs:
			msg += ' '
			msg += ' '.join(attrs)
		msg += '> no MainTraversor method'
		self.gen.debugSection.append(msg, self.getAttr(node, 'stack:file'))
		return True


class CleaningTraversor(Traversor):
	"""Last Pass

	"""

	def traverse(self, node):
		"""<*>

		stack:gc="true" means garabage collect the node.
		
		Any previous traversal can set this attribute
		to have the tag removed from the tree.

		"""

		gc = self.getAttr(node, 'stack:gc')
		gc = str2bool(gc)

		if gc:
			self.removeNode(node)
		return True


		
class Generator:
	"""Base class for various DOM based kickstart graph generators.
	The input to all Generators is assumed to be the XML output of KPP."""
	
	def __init__(self):
		self.attrs		= {}
		self.arch		= None
		self.os			= None
		self.profileType	= 'native'
		self.rcsFiles		= {}
		self.stackiSection	= ProfileSection()
		self.debugSection	= ProfileSection()
		self.shellSection	= ProfileSection()
		self.packageSet		= PackageSet()
		self.log		= '/var/log/stack-install.log'
		self.doc                = None
		self.root		= None

	def setArch(self, arch):
		self.arch = arch
		
	def getArch(self):
		return self.arch
	
	def setOS(self, osname):
		self.os = osname
		
	def getOS(self):
		return self.os

	def setProfileType(self, profileType):
		self.profileType = profileType
		
	def getProfileType(self):
		return self.profileType

	def post(self):
		"""Called after the parsing is completed

		"""
		pass

	def traversors(self):
		"""Returns a list of Traversor that derived classes can change.

		"""
		return [ MainTraversor(self) ]

	def parse(self, xml_string):
		debug     = False # write files after each traversal
		i         = 0
		self.doc  = xml.dom.minidom.parseString(xml_string)
		self.root = self.doc.getElementsByTagName('stack:profile')[0]

		if debug:
			fout = open('/tmp/gen-%d-pre.xml' % i, 'w')
			fout.write(self.root.toxml())
			fout.close()
			i += 1

		traversors = [ ]
		traversors.append(SetupTraversor(self))
		traversors.append(PruningTraversor(self))
		traversors.append(ExpandingTraversor(self))
		traversors.extend(self.traversors())
		traversors.append(CleaningTraversor(self))

		for traversor in traversors:
			traversor.pre()
			self.traverse(traversor, self.root)
			traversor.post()
			if debug:
				fout = open('/tmp/gen-parse-%d-%s.%s.xml' % 
					    (i, 
					     traversor.__module__,
					     traversor.__class__.__name__), 'w')
				fout.write(self.root.toxml())
				fout.close()
				i += 1

		self.post()


	def traverse(self, traversor, node):
		return self._traverse(traversor, node)

	def _traverse(self, traversor, node):

		if not node.nodeType == node.ELEMENT_NODE:
			return

		ns  = node.prefix
		tag = node.localName

		# Lookup the handler and run it, then continue to
		# recurse unless the handler returns False.

		try:
			fn = getattr(traversor, 'traverse_%s_%s' % (ns, tag))
		except AttributeError:
			try:
				fn = getattr(traversor, 'traverse_%s' % ns)
			except AttributeError:
				try:
					fn = getattr(traversor, 'traverse')
				except AttributeError:
					fn = lambda node: False

		if not fn(node):
			return

		children = node.childNodes
		for child in children:
			self._traverse(traversor, child)



	def generate(self, section):
		"""Dump the requested section of the kickstart file.  If none 
		exists do nothing."""
		list = []
		try:
			f = getattr(self, "generate_%s" % section)
		except AttributeError:
			f = None
		if f:
			list += f()

		return list

	def generate_stacki(self):
		return self.stackiSection.generate()

	def generate_debug(self):
		return self.debugSection.generate()

	def generate_bash(self):
		profile  = [ '#! /bin/bash' ]
		profile.extend(self.shellSection.generate())
		return profile


class ProfileHandler(handler.ContentHandler,
		     handler.DTDHandler,
		     handler.EntityResolver,
		     handler.ErrorHandler):

	def __init__(self):
		handler.ContentHandler.__init__(self)
		self.recording = False
		self.text      = ''
		self.chapters  = {}
		self.chapter   = None

	def startElement(self, name, attrs):
		if name == 'chapter':
			self.chapter   = self.chapters[attrs.get('name')] = []
			self.recording = True

	def endElement(self, name):
		if self.recording:
			self.chapter.append(self.text)
			self.text = ''

		if name == 'chapter':
			self.recording = False

	def characters(self, s):
		if self.recording:
			self.text += s

	def getChapter(self, chapter):
		doc = []
		if chapter in self.chapters:
			for text in self.chapters[chapter]:
				doc.append(text.lstrip())
		return doc




