# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@


import os
import tempfile
import shutil
import stack
import stack.commands
import string
		
class Command(stack.commands.create.command):
	"""
	Create a RedHat or Solaris package from a given directory.  The
	package will install files in either the same location as the given
	directory, or a combination of the directory basename and the
	provided prefix.

	<param type='string' name='dir'>
	The source directory of the files used to create the OS-specific
	package.
	</param>

	<param type='string' name='name'>
	The name of the package
	</param>

	<param type='string' name='prefix'>
	The prefix pathname prepended to the base name of the source
	directory.
	</param>

	<param type='string' name='version'>
	Version number of the created package (default is current version of Rocks+)
	</param>

	<param type='string' name='release'>
	Release number of the created package (default is '1')
	</param>

	<param type='string' name='rpmextra'>
	Extra RPM directives. These are comma-seperated values that
	are put into the spec files when the RPM is created
	</param>

	<example cmd='create package dir=/opt/stream name=stream'>
	Create a package named stream in the current directory using the
	contents of the /opt/stream directory.  The resulting package will
	install its files at /opt/stream.
	</example>

	<example cmd='create package dir=/opt/stream name=localstream prefix=/usr/local'>
	Create a package named localstream in the current directory using the
	contents of the /opt/stream directory.  The resulting package will
	install its files at /usr/local/stream.
	</example>
	
	<example cmd='createpackage dir=/opt/stream name=stream rpmextra="Requires: iperf, AutoReqProv: no"'>
	Creates the steam package with an RPM "requires" directive on iperf,
	and disables automatic dependency resolution for the package.
	</example>
	"""

	def run(self, params, args):
		dir = None

		(name, dir, prefix, version,
			release, rpmextra) = self.fillParams([
				('name', None, True),
				('dir', None, True),
				('prefix',),
				('version', stack.version),
				('release', '1'),
				('rpmextra','AutoReqProv: no'),
			])

		rocksRoot = os.environ['ROCKSBUILD']

		if not prefix:
			prefix = os.path.split(dir)[0]
		
		tmp = tempfile.mktemp()
		os.makedirs(tmp)
		shutil.copy(os.path.join(rocksRoot,'etc', 'create-package.mk'),
			    os.path.join(tmp, 'Makefile'))
		cwd = os.getcwd()
		os.chdir(tmp)

		file = open(os.path.join(tmp, 'version.mk'), 'w')
		file.write('NAME=%s\n' % name)
		file.write('VERSION=%s\n' % version)
		file.write('RELEASE=%s\n' % release)
		file.write('PREFIX=%s\n' % prefix)
		file.write('SOURCE_DIRECTORY=%s\n' % dir)
		file.write('DEST_DIRECTORY=%s\n' % cwd)

		# Create the RPM.EXTRAS directive that will add
		# extra information to the specfile
		rpm_extras = map(string.strip, rpmextra.split(','))
		rpmextra = string.join(rpm_extras, '\\\\n')
		file.write("RPM.EXTRAS=\"%s\"\n" % rpmextra)
		file.close()

		for line in os.popen('make dir2pkg').readlines():
			self.addText(line)

		shutil.rmtree(tmp)
		

