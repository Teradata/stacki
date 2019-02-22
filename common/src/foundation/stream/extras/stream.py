# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import subprocess
import re
import os


def __virtual__():
	return "stream"


def run():
	cmd = ''

	if os.path.exists('/opt/stack/bin/stream_c.exe'):
		cmd = '/opt/stack/bin/stream_c.exe'
	elif os.path.exists('/opt/stream/bin/stream'):
		cmd = '/opt/stream/bin/stream'

	p = subprocess.Popen([ cmd ], stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)

	op = []
	o, e = p.communicate()
	whitelist = [
		re.compile('^Copy:'),
		re.compile('^Scale:'),
		re.compile('^Add:'),
		re.compile('^Triad:')
	]
	for i in o.split('\n'):
		match = False
		res = {}
		for w in whitelist:
			if w.match(i):
				match = True
				break
		if match is False:
			continue
		t = i.split()
		res['test'] = t[0].strip(':').lower()
		res['best'] = t[1].strip()
		res['avg'] = t[2].strip()
		res['min'] = t[3].strip()
		res['max'] = t[4].strip()
		op.append(res)

	return op
