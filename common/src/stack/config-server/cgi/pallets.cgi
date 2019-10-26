#!/opt/stack/bin/python3

"""
The purpose of this script is to support 'central' installs.

During installation of a stacki frontend, in the wizard you can
add additional pallets from another server which is serving this
script.

Since all pallets are given a roll-*.xml file once they are added
to stacki, we can just use probepal to get the info we need.
"""

import json
import stack.probepal

pallet_dir = '/export/stack/pallets'

pallet_info = []
pal = stack.probepal.Prober()
pallets = pal.find_pallets(pallet_dir)
for p in pallets[pallet_dir]:
	pallet_info.append({
		'name': p.name,
		'version': p.version,
		'release': p.release,
		'arch': p.arch,
		'os': p.distro_family,
	})

pallet_info = json.dumps(pallet_info)

print('Content-type: application/json')
print('Content-length: {}'.format(len(pallet_info)))
print('')
print(pallet_info)
