#!/opt/stack/bin/python3
#
# this program is used to check that all the packages for a roll are built
# when 'make roll' is run
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import os
import sys
import stack.file
import stack.util

if len(sys.argv) < 3:
	print('error - use make manifest-check')
	sys.exit(1)

palletname = sys.argv[1]
buildpath  = sys.argv[2]

try:
	secondary = sys.argv[3]
except:
	secondary = None

try:
	release = sys.argv[4]
except:
	release = None

tree = stack.file.Tree(os.getcwd())

builtfiles = []
for arch in [ 'noarch', 'i386', 'x86_64', 'armv7hl' ]:
	path = os.path.join(buildpath, 'RPMS', arch)
#	print('searching %s' % path)
	found = tree.getFiles(path)
#	print('found %d files' % len(found))
	builtfiles += found

manifests = [ ]
search    = [ 'common', '.' ]
if secondary:
	search.append(secondary)

for path in search:
	filename = os.path.join(path, 'manifest')
	if os.path.exists(filename):
		manifests.append(filename)

	dirname = os.path.join(path, 'manifest.d')
	if os.path.exists(dirname):
		for filename in os.listdir(dirname):
			name, ext = os.path.splitext(filename)
			if ext == '.manifest':
				manifests.append(os.path.join(dirname, filename))
			elif release and ext == '.%s' % release:
				manifests.append(os.path.join(dirname, filename))

packages = { }
found    = False
for filename in manifests:
	print('reading %s' % filename)
	found = True
	file = open(filename, 'r')
	for line in file.readlines():
		l = line.strip()
		if len(l) == 0 or (len(l) > 0 and l[0] == '#'):
			continue
		if l[0] == '-': # use '-package' to turn off the check
			print(f'\tdisable {l[1:]}')
			packages[l[1:]] = False
		elif l not in packages:
			print(f'\tenable  {l}')
			packages[l] = True
	file.close()

manifest = [ ]
for pkg in packages:
	if packages[pkg]:
		manifest.append(pkg)

if not found:
	print('Cannot find any manifest files')
	sys.exit(0)

built = []
notmanifest = []

for rpm in builtfiles:
	try:
		pkg = rpm.getPackageName()
		if pkg in manifest:
			if pkg not in built:
				#
				# this check will catch duplicate package
				# basenames -- this occurs when the i386 and
				# x86_64 versions of the same package are in
				# a roll
				#
				built.append(pkg)
		else:
			notmanifest.append(pkg)
	except:
		pass

exit_code = 0
if len(manifest) != len(built):
	print('\nERROR - the following packages were not built:')
	for pkg in manifest:
		if pkg not in built:
			print('\t%s' % pkg)
	exit_code += 1

if len(notmanifest) > 0:
	print('\nERROR - the following packages were built but not in manifest:')
	for pkg in notmanifest:
		print('\t%s' % pkg)
	exit_code += 1

if exit_code == 0:
	print('passed')
sys.exit(exit_code)
