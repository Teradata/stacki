#!/opt/stack/bin/python3 -E
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import os
import random
import re
import subprocess
import sys
import time



# Start to build the curl command
command = [
	'/usr/bin/curl', '--silent', '--write-out', '%{http_code}',
	'--local-port', '1-100', '--output', '/tmp/ks.xml', '--insecure'
]

# Parse the boot args
boot_args = {}
with open('/proc/cmdline') as f:
	for arg in f.readline().split():
		parts = arg.split('=', 1)
		if len(parts) == 1:
			boot_args[parts[0]] = None
		else:
			boot_args[parts[0]] = parts[1]

if 'inst.ks' not in boot_args:
	sys.exit("Error: no inst.ks found!")

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

	# Only add our header if Redhat isn't told to do it
	if 'inst.ks.sendmac' not in boot_args:
		command.extend([
			'--header',
			f'X-RHN-Provisioning-MAC-{ndx}: {device} {mac}'
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

# Append the URL to request
command.append(f'{boot_args["inst.ks"]}?os=redhat&arch=x86_64&np={os.cpu_count()}')

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
