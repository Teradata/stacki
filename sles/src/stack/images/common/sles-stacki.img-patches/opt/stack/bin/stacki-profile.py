#!/opt/stack/bin/python3 -E
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import json
import os
import random
import re
import subprocess
import sys
import time


with open('/tmp/stacki-profile.debug', 'w') as debug:
	for key, value in os.environ.items():
		debug.write(f'{key} {value}\n')

# Start to build the curl command
command = [
	'/usr/bin/curl', '--silent', '--write-out', '%{http_code}',
	'--local-port', '1-100', '--output', '/tmp/stacki-profile.xml',
	'--insecure'
]

# Load ib_ipoib driver to include IB information
subprocess.call(["/sbin/modprobe","ib_ipoib"])

# Get the interfaces to report back the device and macs
result = subprocess.run(
	['ip', '-oneline', 'link', 'show'],
	capture_output=True,
	universal_newlines=True
)

ndx=0
for line in result.stdout.splitlines():
	device, link, mac = re.match(r"""
		\d+:\s+         # Index
		(\S+)           # Device name
		:\s.+           # Junk we don't care about
		link/(\S+)\s+   # The link type
		([0-9a-f:]+)\s  # The MAC address
	""", line, re.VERBOSE).groups()

	if link == 'loopback':
		continue

	command.extend([
		'--header', f'X-RHN-Provisioning-MAC-{ndx}: {device} {mac}'
	])

	ndx += 1

# Get the IPMI mac if we can
result = subprocess.run(
	['/usr/bin/ipmitool', 'lan', 'print', '1'],
	capture_output=True,
	universal_newlines=True
)

for line in result.stdout.splitlines():
	if line.startswith("MAC Address"):
		mac = line.split(":", 1)[1].strip()
		command.extend([
			'--header', f'X-RHN-Provisioning-MAC-{ndx}: ipmi {mac}'
		])

		break

# Get the number of CPUs
with open('/proc/cpuinfo') as f:
	cpus = len(re.findall(r'^processor\s+:\s+\d+', f.read(), re.MULTILINE))

# Find the frontend server
server = os.environ.get('Server', None)
if not server:
	with open('/proc/cmdline') as f:
		for arg in f.readline().split():
			parts = arg.split('=', 1)
			if parts[0].strip() == 'Server':
				server = parts[1].strip()

if not server:
	# No server found on boot line, so maybe we are in AWS and can find
	# it from the user-data json.
	result = subprocess.run(
		['/usr/bin/curl', 'http://169.254.169.254/latest/user-data'],
		capture_output=True,
		universal_newlines=True
	)

	try:
		data = json.loads(result.stdout)
	except:
		data = {}

	server = data.get('master')

# Append the URL to request
if not server:
	sys.exit("Error: no server found!")

command.append(
	f'https://{server}/install/sbin/profile.cgi'
	f'?os=sles&arch=x86_64&np={cpus}'
)

# Retry until we get an installation file
while True:
	result = subprocess.run(
		command, capture_output=True, universal_newlines=True
	)

	try:
		http_code = int(result.stdout.splitlines()[0])

		if http_code == 204:
			# We aren't doing the install so power down
			os.system("poweroff --force")

			# Give it a minute to power down
			time.sleep(60)

		elif http_code == 200:
			# It worked!
			break

	except (ValueError, IndexError):
		pass

	# No luck, try again in a bit
	time.sleep(random.randint(3, 10))
