import stack.api as api

def test_stack_list_boxes():	
	output = api.Call('list box')
	hdr = '\n\nNAME    OS     PALLETS                     CARTS'
	print(hdr)
	for o in output:
		vals = [ str(v) for v in o.values()]
		print(' '.join(vals))


def test_stack_list_pallets():	
	output = api.Call('list pallet')
	hdr = '\n\nNAME   VERSION RELEASE ARCH   OS     BOXES'
	print(hdr)
	for o in output:
		vals = [ str(v) for v in o.values()]
		print(' '.join(vals))

def test_stack_list_networks():	
	output = api.Call('list network')
	hdr = '\n\nNETWORK ADDRESS     MASK          GATEWAY      MTU  ZONE  DNS   PXE'
	print(hdr)
	for o in output:
		vals = [ str(v) for v in o.values()]
		print(' '.join(vals))


def test_stack_list_host():	
	output = api.Call('list host')
	hdr = '\n\nHOST RACK RANK APPLIANCE OS BOX ENVIRONMENT OSACTION INSTALLACTION STATUS'
	print(hdr)
	for o in output:
		vals = [ str(v) for v in o.values()]
		print(' '.join(vals))

