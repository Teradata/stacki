#!/opt/stack/bin/python

import sys
import os

sys.path.append('/tmp')
from stack_site import *

tgt = sys.argv[1]

if tgt == 'intarget':
	rdir = '/target/'
else:
	rdir = '/'

for k,v in ssh_keys.iteritems():

	if k == 'authorized_key':
		fname = '%sroot/.ssh/authorized_keys' % rdir
		f = open(fname, 'w')	
		f.write(ssh_keys[k])
		os.chmod(fname, 0o600)
		f.close()
	else:
		fname = '%setc/ssh/ssh_host_%s' % (rdir,k)
		f = open(fname, 'w')	
		f.write(ssh_keys[k])
		f.close()
		if 'pub' in k:
			os.chmod(fname, 0o444)
		else:
			os.chmod(fname, 0o400)
