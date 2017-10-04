#! /usr/bin/python2

# Note that this script requires the yum module which only runs on Python2
# no point in trying to port to py3 as it ships with yum and is going to be deprecated in favor of dnf

import sys
import yum
import json
#
# use yum to resolve dependencies
#

yumconf = sys.argv[1]
rpms = sys.argv[2:]

a = yum.YumBase()
a.doConfigSetup(fn='%s' % yumconf, init_plugins=False)
a.conf.cache = 0
a.doTsSetup()
a.doRepoSetup()
a.doRpmDBSetup()
a.doSackSetup()
a.doGroupSetup()
selected = []
for rpm in rpms + [ '@base', '@core' ]:
	if rpm[0] == '@':
		group = a.comps.return_group(
			rpm[1:].encode('utf-8'))
		for r in group.mandatory_packages.keys() + group.default_packages.keys():
			if r not in selected:
				selected.append(r)
	elif rpm not in selected:
		selected.append(rpm)

pkgs = []
avail = a.pkgSack.returnNewestByNameArch()
for p in avail:
	if p.name in selected:
		pkgs.append(p)

done = 0
while not done:
	done = 1
	results = a.findDeps(pkgs)
	for pkg in results.keys():
		for req in results[pkg].keys():
			reqlist = results[pkg][req]
			for r in reqlist:
				if r.name not in selected:
					selected.append(r.name)
					pkgs.append(r)
					done = 0

print(json.dumps(selected))
