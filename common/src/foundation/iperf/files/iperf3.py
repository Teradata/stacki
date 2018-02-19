#!/opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import os
import sys
import subprocess
import json

def run(home, away):
	#
	# get my index into the 'hosts' array
	#
	client = away
	s = subprocess.Popen(['iperf3',
		'-J', '-t', '5', '-c', client],
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	o, e = s.communicate()

	j = json.loads(o)

	file = open('/tmp/nettest.debug', 'w')
	file.write('j : %s\n\n' % j)

	output = {}
	output['home'] = home
	output['away'] = client

	out = j['end']['streams'][0]
	file.write('out : %s\n\n' % out)

	try:
		output['sent'] = out['sender']['bits_per_second']
	except:
		output['sent'] = '0.0'

	try:
		output['recv'] = out['receiver']['bits_per_second']
	except:
		output['recv'] = '0.0'

	file.write('%s\n' % output)
	file.close()

	return output

array = sys.argv[1:]
home = array[0]
away = array[1]
output = run(home,away)
print(output)
