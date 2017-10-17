#!/opt/stack/bin/python3
# @SI_Copyright@
# Copyright (c) 2006 - 2014 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @SI_Copyright@
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
