#!/opt/stack/bin/python3

import os
import os.path
import json

pallet_dir = '/export/stack/pallets'
pallet_tree = []

def getPalletTree(rootdir, depth):
	dirs = [os.path.join(rootdir, x) for x in os.listdir(rootdir)]
	dirs = [x for x in dirs if os.path.isdir(x)]
	
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
			'name': name,
			'version': version,
			'release': release,
		})
	return pallet_info

getPalletTree(pallet_dir, 2)
pallet_info = json.dumps(getPalletInfo())

print('Content-type: application/json')
print('Content-length: {}'.format(len(pallet_info)))
print('')
print(pallet_info)
