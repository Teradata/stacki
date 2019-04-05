import sys
from operator import attrgetter

import common

# general:
# this package allows for fingerprinting a directory to determine if it contains a stacki pallet
# the design allows for the dynamic discovery of additional finderprinting probes,
# along with a means of weighting which probes are used first as well as catching partial matches
# probes can be added by creating a new python module whose name begins with `prober_` and which
# has a subclass of the Probe class.  See common.py for more detail. 


if __name__ == '__main__':
	prober = common.Prober()

	debug = False
	if sys.argv[1] == '--debug':
		debug = True
		print('debug=True')
		del sys.argv[1]

	print_debug = print if debug else lambda *a, **k: None

	args = sys.argv[1:]
	prober.find_pallets(*args)
