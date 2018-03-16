# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import time
from stack.api import Call, ReturnCode

ENVIRONMENT = 'pytest'


def setup_module(module):
	Call('remove host e:%s' % ENVIRONMENT, stderr=False)
	Call('add environment %s' % ENVIRONMENT)
			
def teardown_module(module):
	Call('remove environment %s' % ENVIRONMENT)


def setup_hosts(numHosts):
	rackSize  = 40

	t0 = time.time()
	rank = rack = 999 # start at rack 1000 (yeah I know this could be smarter)
	for i in range(0, numHosts):
		if rank >= rackSize:
			rank  = 0
			rack += 1
		hostname = 'backend-%d-%d' % (rack, rank)
		Call('add host %s environment=%s' % (hostname, ENVIRONMENT))
		rank += 1
	t = (time.time() - t0)
	print('add host'.ljust(32), '%.3fs' % t)

	result = Call('list host e:%s' % ENVIRONMENT)
	assert ReturnCode() == 0 and len(result) == (numHosts)

def teardown_hosts():
	t0 = time.time()
	Call('remove host e:%s' % ENVIRONMENT, stderr=False)
	t = (time.time() - t0)
	print('remove host'.ljust(32), '%.3fs' % t)




def test_scale():
	print()

	for size in [ 10, 20, 30, 40, 100, 1000 ]:
		print('size = %d' % size)

		setup_hosts(size)

		t0 = time.time()
		rows = Call('list host e:%s' % ENVIRONMENT)
		t = (time.time() - t0)
		print('list host'.ljust(32), '%.3fs' % t)

		assert rows[0]['host'] # grab the first hostname
		t0 = time.time()
		Call('list host profile', [ rows[0]['host'] ])
		t = (time.time() - t0)
		print('list host profile'.ljust(32), '%.3fs' % t)

		teardown_hosts()


		
	




