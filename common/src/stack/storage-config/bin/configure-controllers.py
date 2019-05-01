#!/opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import sys
from subprocess import CalledProcessError

sys.path.append('/tmp')
from stack_site import *

sys.path.append('/opt/stack/lib')
from stacki_storage import *

from stack.bool import str2bool

##
## functions
##

def sortids(entry):
	try:
		v = int(entry)
	except:
		v = sys.maxsize

	return v


def getController():
	# Check if a controller is listed explicitly
	controller_type = None
	if 'storage.adapter.type' in attributes:
		controller_type = attributes['storage.adapter.type']

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

##
## MAIN
##

# Halt the install with an error message on the console and in the message queue
# if we are unable to create a RAID.
# To override, set the attribute 'halt_install_on_error=False'.

halt_on_error  = str2bool(attributes.get('halt_install_on_error', True))
nukecontroller = str2bool(attributes.get('nukecontroller', False))
secureerase    = str2bool(attributes.get('secureerase', False))

#
# if 'secureerase' is true, then that implies that 'nukecontroller' is true
#
if secureerase:
	nukecontroller = True
	
#
# only run this code if 'nukecontroller' is true
#
if not nukecontroller:
	sys.exit(0)

# Get the Controller Object, the adapter info,

(ctrl, adapter) = getController()

if ctrl == None:
	sys.exit(0)

if adapter == None:
	sys.exit(0)

#
# if no csv_controller data, then just exit
#
if not csv_controller:
	sys.exit(0)

#
# reconstruct the arrays
#
arrayids = []
for o in csv_controller:
	arrayid = o['arrayid']
	if arrayid not in arrayids:
		arrayids.append(o['arrayid'])

arrayids.sort(key = sortids)

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
			options	 = o['options']

	if not adapter:
		adapter = ctrl.getAdapter()
	if not enclosure:
		enclosure = ctrl.getEnclosure(adapter)

	ea = '%s:%s' % (enclosure, adapter)

	if ea not in nuked:
		ctrl.doNuke(enclosure, adapter)
		nuked.append(ea)
		freeslots[adapter] = ctrl.getSlots(adapter)

		for slot in freeslots[adapter]:
			if secureerase:
				ctrl.doSecureErase(enclosure, adapter, slot)

	slots.sort(key = sortids)

	if len(slots) == 1 and slots[0] == '*':
		#
		# skip for now, we'll do these disks at the very end
		#
		continue

	try:
		if raidlevel == 'hotspare' and arrayid == 'global':
			ctrl.doGlobalHotSpare(adapter, enclosure, hotspares, options, check=halt_on_error)
		else:
			ctrl.doRaid(raidlevel, adapter, enclosure, slots, hotspares, options, check=halt_on_error)
	except CalledProcessError as e:
		print(' '.join(e.cmd))
		print(f'output: {e.stdout}')
		sys.exit(1)

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
	if 'slot' in o.keys() and o['slot'] == '*':
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
				raidlevel = '0'

		if 'options' in o.keys():
			try:
				options = o['options']
			except:
				options = ''

		if not adapter:
			adapter = ctrl.getAdapter()
		if not enclosure:
			enclosure = ctrl.getEnclosure(adapter)

		if 'arrayid' in o.keys():
			try:
				if o['arrayid'] == '*':
					if raidlevel == '1':
						#
						# special case for arrayid == '*' and raidlevel 1 -- put the remaining
						# disks into RAID 1 pairs
						#
						while len(freeslots[adapter]) > 1:
							disks = [ freeslots[adapter][0], freeslots[adapter][1] ]
							ctrl.doRaid(1, adapter, enclosure, disks, [], options, check=halt_on_error)

							freeslots[adapter].remove(disks[0])
							freeslots[adapter].remove(disks[1])
					else:
						# JBOD Mode for the remainder
						for slot in freeslots[adapter]:
							ctrl.doRaid(0, adapter, enclosure, [ slot ],
								[], options, check=halt_on_error)

				# RAID mode - Single array for remaining disks
				else:
					ctrl.doRaid(raidlevel, adapter, enclosure, freeslots[adapter],
						hotspares, options, check=halt_on_error)
			except CalledProcessError as e:
				print(' '.join(e.cmd))
				print(f'output: {e.stdout}')
				sys.exit(1)
