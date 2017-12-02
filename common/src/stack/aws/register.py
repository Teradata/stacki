#!/opt/stack/bin/python3
#
# @copyright@
# @copyright@

import subprocess
import json


def Lookup(path):
	p = subprocess.Popen(['/usr/bin/curl', 'http://169.254.169.254/latest/%s' % path],
			     stdout=subprocess.PIPE,
			     stderr=subprocess.PIPE)
	o, e = p.communicate()
	return o.decode()


user = json.loads(Lookup('user-data'))
args = []

args.append('ami=%s'	  % Lookup('meta-data/ami-id'))
args.append('zone=%s'	  % Lookup('meta-data/placement/availability-zone'))
args.append('instance=%s' % Lookup('meta-data/instance-id'))
args.append('hostname=%s' % Lookup('meta-data/hostname').split('.')[0])
args.append('box=%s'	  % user['box'])
args.append('ip=%s'	  % Lookup('meta-data/local-ipv4'))
args.append('mac=%s'	  % Lookup('meta-data/mac'))

p = subprocess.Popen(['/usr/bin/curl', '-s',
		      '--local-port', '1-100',
		      '--insecure',
		      'https://%s/install/sbin/register.cgi?%s' % (user['master'], '&'.join(args))],
		     stdout=subprocess.PIPE,
		     stderr=subprocess.PIPE)
o, e = p.communicate()

s = o.decode()
print(s)
