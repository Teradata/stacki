#!/opt/stack/bin/python

import os
import os.path
import json

pallet_dir = '/export/stack/pallets'

pallet_tree = []
level = 2

f = lambda x: os.path.isdir(x)


def getPalletTree(rootdir, depth):
	dirs = [os.path.join(rootdir,d) for d in os.listdir(rootdir)]
	dirs = filter(f, dirs)
	if depth > 0:
		for directory in dirs:
			getPalletTree(directory, depth - 1)
	else:
		pallet_tree.extend(dirs)


def getPalletInfo():
	pallet_info = []
	for pallet in pallet_tree:
		pallet = os.path.normpath(pallet)
		pi = pallet.split('/')
		release = pi[-1]
		version = pi[-2]
		name    = pi[-3]
		pallet_info.append({
			'name':name,
			'version':version,
			'release':release,
		})
	return pallet_info

getPalletTree(pallet_dir, level)
pallet_info = getPalletInfo()

out = ''
out += json.dumps(pallet_info)

print 'Content-type: application/json'
print 'Content-length: %d' % len(out)
print ''
print out
