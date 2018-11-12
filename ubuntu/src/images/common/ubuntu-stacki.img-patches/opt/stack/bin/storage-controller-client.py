#!/opt/stack/bin/python

import sys
sys.path.append('/opt/stack/lib')

sys.path.append('/tmp')
from stack_site import *


def str2bool(s):
	if s and s.upper() in [ 'ON', 'YES', 'Y', 'TRUE', '1' ]:
		return 1
	else:
		return 0

def getController():

	# Check if a controller is listed explicitly
	if attributes.has_key('storage.adapter.type'):
		controller_type = attributes['storage.adapter.type']
	else:
		controller_type = None

	# If controller type is specified, make that
	# the only possible choice. Otherwise, list
	# all controllers supported by StackI.
	if controller_type:
		ctrl_list = [ controller_type ]
	else:
		ctrl_list = ['storcli', 'megacli', 'hpssacli']

	# For all the controllers in the list, cycle
	# through them to see which adapter is connected.
	for c in ctrl_list:
		# We will always correctly import one of the default
		# controllers. If we fail to import one, then it's
		# an invalid controller that isn't supported, and
		# we bail out.
		try:
			modulename = 'controller_%s' % c
			controller = __import__(modulename)
		except ImportError:
			return (None, None)


		# Once we import, get the CLI, adapter
		ctrl = controller.CLI()
		adapter = ctrl.getAdapter()

		if adapter != None:
			return (ctrl, adapter)

	return(None, None)

#
# only run this code if 'nukecontroller' is true
#
if not str2bool(attributes['nukecontroller']):
	sys.exit(0)

# Get the Controller Object, the adapter info,

(ctrl, adapter) = getController()


if ctrl == None:
	sys.exit(0)

if adapter == None:
	sys.exit(0)

#
# if no output, then just nuke the first adapter and exit
#
if not csv_controller:
	ctrl.doNuke(adapter)
	sys.exit(0)


#
# reconstruct the arrays
#
arrayids = []
for o in csv_controller:
	arrayid = o['arrayid']
	if arrayid not in arrayids:
		arrayids.append(o['arrayid'])

arrayids.sort()

nuked = []
freeslots = {}

for arrayid in arrayids:
	slots = []
	hotspares = []
	raidlevel = None
	enclosure = None
	adapter = None
	options = ''
		
	for o in csv_controller:
		if o['arrayid'] != arrayid:
			continue

		if 'slot' in o.keys():
			if 'raidlevel' in o.keys() and \
					o['raidlevel'] == 'hotspare':
				hotspares.append(o['slot'])
			else:
				slots.append(o['slot'])

		if 'adapter' in o.keys() and not adapter:
			try:
				adapter = int(o['adapter'])
			except:
				adapter = None
		if 'enclosure' in o.keys() and not enclosure:
			try:
				enclosure = o['enclosure']
			except:
				enclosure = None
		if 'raidlevel' in o.keys() and not raidlevel:
			raidlevel = o['raidlevel']

		if 'options' in o.keys():
			options  = o['options']

	if not adapter:
		adapter = ctrl.getAdapter()
	if not enclosure:
		enclosure = ctrl.getEnclosure(adapter)

	if adapter not in nuked:
		ctrl.doNuke(adapter)
		nuked.append(adapter)
		freeslots[adapter] = ctrl.getSlots(adapter)

	slots.sort()

	if len(slots) == 1 and slots[0] == '*':
		#
		# skip for now, we'll do these disks at the very end
		#
		continue

	if raidlevel == 'hotspare' and arrayid == 'global':
		ctrl.doGlobalHotSpare(adapter, enclosure, hotspares, options)
	else:
		ctrl.doRaid(raidlevel, adapter, enclosure, slots, hotspares,
			options)

	for slot in slots + hotspares:
		try:
			freeslots[adapter].remove(slot)
		except:
			pass


#
# lastly, do the wildcard entries (slot = '*' and arrayid = '*')
#
adapter = None
enclosure = None
raidlevel = None
hotspares = []
options = ''

for o in csv_controller:
	if 'arrayid' in o.keys() and o['arrayid'] == '*' and \
			'slot' in o.keys() and o['slot'] == '*':

		if 'adapter' in o.keys():
			try:
				adapter = int(o['adapter'])
			except:
				adapter = None

		if 'enclosure' in o.keys():
			try:
				enclosure = o['enclosure']
			except:
				enclosure = None

		if 'raidlevel' in o.keys():
			try:
				raidlevel = o['raidlevel']
			except:
				raidlevel = 0

		if 'options' in o.keys():
			try:
				options = o['options']
			except:
				options = ''

		if not adapter:
			adapter = ctrl.getAdapter()
		if not enclosure:
			enclosure = ctrl.getEnclosure(adapter)

		for slot in freeslots[adapter]:
			ctrl.doRaid(raidlevel, adapter, enclosure, [ slot ],
				hotspares, options)


