#! /opt/stack/bin/python3
#
# @copyright@
# @copyright@

import sys
import time
import ipaddress
import netifaces
import urllib.error
from urllib.request import urlopen
from stack.bool import str2bool
from stack.api import Call

def lookup(path):
	done = False
	while not done:
		try:
			response = urlopen('http://169.254.169.254/latest/%s' % path)
			done	 = True
		except urllib.error.HTTPError:
			time.sleep(1)
	value = response.read().decode()
	return value

aws = False
for row in Call('list.host.attr', [ 'localhost', 'attr=aws' ]):
	aws = str2bool(row['value'])
if not aws:
	print('not inside amazon')
	sys.exit(0)

found = False
key   = lookup('meta-data/public-keys/0/openssh-key').strip()
with open('/root/.ssh/authorized_keys', 'r') as f:
	for line in f.readlines():
		if key == line.strip():
			found = True
if not found:
	with open('/root/.ssh/authorized_keys', 'a') as f:
		f.write('%s\n' % key)


public_ipv4	= lookup('meta-data/public-ipv4')
public_hostname = lookup('meta-data/public-hostname')

(gw_ip, gw_dev) = netifaces.gateways()['default'][netifaces.AF_INET]

for dev in netifaces.interfaces():
	if dev !=  gw_dev:
		continue
	addrs	  = netifaces.ifaddresses(dev)
	mac	  = addrs[netifaces.AF_LINK][0]['addr']
	ip	  = addrs[netifaces.AF_INET][0]['addr']
	mask	  = addrs[netifaces.AF_INET][0]['netmask']
	broadcast = addrs[netifaces.AF_INET][0]['broadcast']

net = ipaddress.IPv4Network('%s/%s' % (ip, mask), strict=False)


Call('set.host.interface.mac', [ 'localhost', 'interface=%s' % dev, 'mac=%s' % mac ])
Call('set.host.interface.ip',  [ 'localhost', 'interface=%s' % dev, 'ip=%s'  % ip  ])

Call('set.network.address', [ 'private', 'address=%s' % net.network_address ])
Call('set.network.mask',    [ 'private', 'mask=%s'    % mask	])
Call('set.network.gateway', [ 'private', 'gateway=%s' % gw_ip	])

Call('set.attr', [ 'attr=aws', 'value=true' ])
Call('set.attr', [ 'attr=Kickstart_PrivateNTPHost', 'value=%s' % ip ])

Call('sync.config')

