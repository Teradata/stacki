#! /opt/stack/bin/python3
'''
This package allows for fingerprinting a directory to determine if it contains a stacki pallet
the design allows for the dynamic discovery of additional finderprinting probes,
along with a means of weighting which probes are used first.

probes can be added by creating a new python module whose name begins with `prober_` and which
has a subclass of the Probe class.  See probepal/common.py for more detail. 
'''


import sys
import json
from operator import attrgetter
import dataclasses

import stack.probepal

class EnhancedJSONEncoder(json.JSONEncoder):
	''' make dataclasses serializable '''
	def default(self, o):
		if dataclasses.is_dataclass(o):
			return dataclasses.asdict(o)
		return super().default(o)

if __name__ == '__main__':
	prober = stack.probepal.Prober()

	debug = False
	for i, arg in enumerate(sys.argv):
		if arg == '--debug':
			debug = True
			del sys.argv[i]
			break

	print_debug = print if debug else lambda *a, **k: None

	results = {}
	for arg in sys.argv[1:]:
		print_debug(f'====== probing {arg} ======')
		match = prober.find_pallets(arg)
		if not match[arg]:
			print_debug('unable to identify pallet')
		results.update(match)

	print(json.dumps(results, cls=EnhancedJSONEncoder, indent=4))
