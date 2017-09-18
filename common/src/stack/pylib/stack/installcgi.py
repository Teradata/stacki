#! /opt/stack/bin/python
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.16  2010/09/07 23:53:08  bruno
# star power for gb
#
# Revision 1.15  2009/05/01 19:07:08  mjk
# chimi con queso
#
# Revision 1.14  2009/03/04 01:32:13  bruno
# attributes work for frontend installs
#
# Revision 1.13  2008/10/18 00:56:02  mjk
# copyright 5.1
#
# Revision 1.12  2008/05/30 22:15:16  bruno
# can now install a frontend off CD with the distro moved to
# /export/stack/install
#
# Revision 1.11  2008/05/22 21:02:07  bruno
# rocks-dist is dead!
#
# moved default location of distro from /export/home/install to
# /export/stack/install
#
# Revision 1.10  2008/03/24 20:58:44  bruno
# more apache vs. lighttpd directory listing parsing
#
# Revision 1.9  2008/03/06 23:41:44  mjk
# copyright storm on
#
# Revision 1.8  2007/12/10 21:28:35  bruno
# the base roll now contains several elements from the HPC roll, thus
# making the HPC roll optional.
#
# this also includes changes to help build and configure VMs for V.
#
# Revision 1.7  2007/06/23 04:03:24  mjk
# mars hill copyright
#
# Revision 1.6  2006/11/29 23:12:40  bruno
# prototype support for lights out frontend installs
#
#

import os
import os.path
import string
import shutil
import stack.file
import stack.util


class InstallCGI:

	def __init__(self, rootdir=None):
		if rootdir is None:
			self.rootdir = '/export/stack'
		else:
			self.rootdir = rootdir

		cmd = '/opt/stack/bin/stack report version'
		for line in os.popen(cmd).readlines():
			self.version = line[:-1]

		self.arch = stack.util.getNativeArch()

		return


	def createPopt(self, dir=None):
		if dir is None:
			dir = self.rootdir

		if not os.path.exists(dir):
			os.system('mkdir -p %s' % (dir))

		filename = os.path.join(dir, '.popt')

		if not os.path.exists(filename):
			file = open(filename, 'w')
			file.write("rpm alias --dbpath --define '_dbpath !#:+'")
			file.write("\n")
			file.close()

		return


	def getSiteDotAttrs(self):
		#
		# look in the newly built distro for site.attrs
		#
		site_attrs = os.path.join(self.rootdir, 'distributions',
			'default', self.arch, 'build', 'nodes', 'site.attrs')

		if os.path.exists(site_attrs):
			shutil.copy(site_attrs, '/tmp/site.attrs')

		return


	def createSkeletonSiteAttrs(self):
		self.getSiteDotAttrs()
		if os.path.exists('/tmp/site.attrs'):
			return

		file = open('/tmp/site.attrs', 'w')

		#
		# set the language
		#
		cmdline = open('/proc/cmdline', 'r')
		args = string.split(cmdline.readline())
		cmdline.close()

		#
		# the default language
		#
		lang = 'en_US'
		langsupport = 'en_US'

		for arg in args:
			if arg.count('lang='):
				a = string.split(arg, '=')
				if len(a) > 1 and a[1] == 'ko':
					lang = 'ko_KR'
					langsupport = string.join([
						'ko_KR.UTF-8',
						'ko_KR',
						'ko',
						'en_US.UTF-8',
						'en_US'
						])

		file.write('Kickstart_Lang:%s\n' % lang)
		file.write('Kickstart_Langsupport:%s\n' % langsupport)

		file.close()

		return


	def getKickstartFiles(self, roll):
		#
		# for every selected roll, find the roll-{name}-kickstart*rpm
		# file
		#
		cwd = os.getcwd()

		self.createPopt(self.rootdir)

		contribdir = os.path.join(self.rootdir, 'contrib', 'default',
			self.version, self.arch, 'RPMS')

		os.system('mkdir -p %s' % (contribdir))
		os.chdir(contribdir)

		if os.path.exists('/tmp/updates/stack/bin/wget'):
			wget = '/tmp/updates/stack/bin/wget'
		else:
			wget = '/usr/bin/wget'

		(rollname, rollver, rollrel, rollarch, rollurl, diskid) = roll

		url = rollurl + '%s/%s/redhat/%s/RPMS/' % (rollname, rollver,
			rollarch)
		cmd = '%s -O - -nv %s 2> /dev/null' % (wget, url)
		lines = os.popen(cmd).readlines()

		#
		# looking for 'roll-<rollname>-kickstart-*rpm and
		# foundation-comps-*rpm
		#
		f1 = 'roll-%s-kickstart' % rollname
		f2 = 'foundation-comps'

		for line in lines:
			a = string.split(line, '"')

			if a[0] == '<a href=':
				#
				# apache style listing
				#
				filename = a[1]
			elif len(a) > 2 and a[2] == '><a href=':
				#
				# lighttpd style listing
				#
				filename = a[3]
			else:
				continue

			if filename[0:len(f1)] == f1 or \
					filename[0:len(f2)] == f2:
				rpmname = url + filename
				getcmd = '%s --quiet %s' % (wget, rpmname)
				os.system(getcmd)

		os.chdir(cwd)
		return


	def rebuildDistro(self, rollslist):
		cwd = os.getcwd()
		path = os.path.join(self.rootdir, 'distributions')
		if not os.path.exists(path):
			os.system('mkdir -p %s' % path)
		os.chdir(path)
		os.system('echo path = %s > /tmp/stack-create-distro.debug' % path)

		#
		# get a list of the rolls
		#
		rolls = []
		for r in rollslist:
			(rollname, rollversion, rollrel, rollarch, rollurl,
				diskid) = r
			rolls.append('%s,%s' % (rollname, rollversion))

		#
		# build the distro
		#
		pythonpath = None
		if 'PYTHONPATH' in os.environ:
			pythonpath = os.environ['PYTHONPATH']

		os.environ['PYTHONPATH'] = '/tmp/updates'

		cmd = 'HOME=%s ' % self.rootdir
		cmd += '/opt/stack/bin/stack create distribution '
		if len(rolls) > 0:
			cmd += 'pallets="%s" ' % ' '.join(rolls)
		cmd += 'root=%s inplace=true' % self.rootdir
		os.system('echo %s > /tmp/stack-create-distro.debug' % cmd)
		os.system(cmd + ' >> /tmp/stack-create-distro.debug 2>&1')

		if pythonpath:
			os.environ['PYTHONPATH'] = pythonpath

		os.chdir(cwd)

		return

