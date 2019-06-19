#!/opt/stack/bin/python3 -E
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import subprocess
import random
import time
import os
import json
import logging

logging.basicConfig(filename="/var/log/profile.log", format="%(asctime)s %(message)s", level = logging.DEBUG)

def get_ipmi_mac():
	# Get IPMI mac
	mac = None
	p = subprocess.Popen(["/usr/bin/ipmitool", "lan","print","1"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	o, e = p.communicate()

	if not o:
		return None

	for line in o.decode().split('\n'):
		if line.startswith("MAC Address"):
			k, v = line.split(":",1)
			mac = v.strip()

	return mac


logging.debug("Writing debug profile...")
debug = open('/tmp/stacki-profile.debug', 'w')

for i in os.environ:
	debug.write('%s %s\n' % (i, os.environ[i]))

debug.close()

#
# make sure the target directory is there
#
logging.debug("Creating profile directory...")
try:
	os.makedirs('/tmp/profile')
except:
	pass

logging.debug("Getting IPMI MAC...")
ipmi_mac = get_ipmi_mac()

logging.debug("Probing IPMI...")
# to include IB information, load ib_ipoib driver
subprocess.call(["/sbin/modprobe","ib_ipoib"])
#
# get the interfaces
#
linkcmd = [ 'ip', '-oneline', 'link', 'show' ]

logging.debug("Getting interfaces...")
p = subprocess.Popen(linkcmd, stdout = subprocess.PIPE)

interface_number = 0

curlcmd = [ '/usr/bin/curl', '-s', '-w', '%{http_code}', '--local-port', '1-100',
	'--output', '/tmp/stacki-profile.xml', '--insecure' ]

o, e = p.communicate()
output = o.decode()
for line in output.split('\n'):
	interface = None
	hwaddr = None

	tokens = line.split()
	if len(tokens) > 13:
		# print 'tokens: %s' % tokens
		#
		# strip off last ':'
		#
		interface = tokens[1].strip()[0:-1]

		for i in range(2, len(tokens)):
			if str(tokens[i]).startswith('link/') and \
					'loopback' not in tokens[i]:
				#
				# we know the next token is the ethernet MAC
				#
				hwaddr = tokens[i+1]
				break

		if interface and hwaddr:
			curlcmd.append('--header')
			curlcmd.append('X-RHN-Provisioning-MAC-%d: %s %s'
				% (interface_number, interface, hwaddr))

			interface_number += 1

if ipmi_mac:
	curlcmd.append('--header')
	curlcmd.append('X-RHN-Provisioning-MAC-%d: %s %s'
			% (interface_number, "ipmi", ipmi_mac))
#
# get the number of CPUs
#
logging.debug("Getting CPU count...")
numcpus = 0
f = open('/proc/cpuinfo', 'r')
for line in f.readlines():
	l = line.split(':')
	if l[0].strip() == 'processor':
		numcpus += 1
f.close()

logging.debug("Getting server...")
server = os.environ.get('Server', None)
# TODO: how do we send correct cmdline?
server = "10.1.1.169"
if not server:
	logging.debug("Reading commandline...")
	cmdline = open('/proc/cmdline', 'r')
	cmdargs = cmdline.readline()
	cmdline.close()

	for cmdarg in cmdargs.split():
		l = cmdarg.split('=')
		if l[0].strip() == 'Server':
			server = l[1]

if not server:
	# No server found on boot line, so maybe we are in AWS and can find
	# it from the user-data json.
	logging.debug("We think we're in AWS...")
	p = subprocess.Popen([ '/usr/bin/curl', 'http://169.254.169.254/latest/user-data' ],
			     stdout=subprocess.PIPE,
			     stderr=subprocess.PIPE)
	o, e = p.communicate()
	try:
		data = json.loads(o)
	except:
		data = {}
	server = data.get('master')


request = 'https://%s/install/sbin/profile.cgi?os=sles&arch=x86_64&np=%d' % \
	(server, numcpus)
curlcmd.append(request)

#
# retry until we get an installation file. if the HTTP request fails, then sleep
# for a random amount of time (between 3 and 10 seconds) before we retry.
#
http_code = 0
while http_code != 200:
	logging.debug("Fetching profile using command: %s", curlcmd)
	p = subprocess.Popen(curlcmd, stdout=subprocess.PIPE, stderr=open('/dev/null'))

	try:
		http_code = p.stdout.readline()
		logging.info("Curl result: %s", http_code)
		http_code = int(http_code)
	except:
		http_code = 0

	if http_code != 200:
		logging.error(f"Failed to fetch profile with error code {http_code}")
		time.sleep(random.randint(3, 10))

