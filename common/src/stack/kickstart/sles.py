#! /opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import subprocess
import profile
import os
import re
import stack.api

class Profile(profile.ProfileBase):
	def set_mac_interface(self, host, mac, interface):
		stack.api.Call('set.host.interface.interface', [ host,
			'mac=%s' % mac, 'interface=%s' % interface ])

	def process_next_mac(self, host, macs, lastmac, deviceid):
		#
		# convert the lastmac string into an integer. we'll use this to find the 'next' mac
		#
		lastmacint = int(lastmac.replace(':', ''), 16)

		foundmac = None
		for mac in macs:
			macint = int(mac.replace(':', ''), 16)
			if macint == lastmacint + 1:
				foundmac = mac
				break

		#
		# if we didn't find the 'next' mac, then just take the first MAC in the list
		#
		if not foundmac:
			foundmac = macs[0]

		self.set_mac_interface(host, foundmac, 'eth%d' % deviceid)

		macs.remove(foundmac)
		return macs, foundmac

	def force_eth0(self, host):
		#
		# collect only the ethernet devices
		#
		macs = []
		for i in os.environ:
			if re.match('HTTP_X_RHN_PROVISIONING_MAC_[0-9]+', i):
				devinfo = os.environ[i].split()
				iface	= devinfo[0]
				macaddr = devinfo[1].lower()

				if len(macaddr.split(':')) == 6 and iface != 'ipmi':
					macs.append(macaddr)

		#
		# in the database, find the interface that is mapped to the 'primary' network
		#
		lastmac = None
		for o in stack.api.Call('list.host.interface', [ host ]):
			if o['network'] == 'primary':
				if o['interface'] == 'eth0':
					#
					# nothing to do -- eth0 is already the primary
					#
					return
				else:
					self.set_mac_interface(host, o['mac'], 'eth0')
					lastmac = o['mac']
					macs.remove(lastmac)
					break

		#
		# if we made it here, we need to reorder all the other ethernet interfaces
		#
		deviceid = 1

		while (macs):
			macs, lastmac = self.process_next_mac(host, macs, lastmac, deviceid)
			deviceid += 1

	def main(self, client):
		output = stack.api.Call('list host attr',
			[ client.addr, 'attr=profile.force_eth0' ])

		if output:
			row = output[0]

			if 'value' in row and stack.bool.str2bool(row['value']):
				try:
					self.force_eth0(client.addr)
				except:
					pass

		p = subprocess.run(['/opt/stack/bin/stack', 'list', 'host', 'xml', client.addr ],
				   stdout=subprocess.PIPE,
				   stderr=subprocess.PIPE)
		rc  = p.returncode
		doc = [ ]

		if rc == 0:
			doc.append('Content-type: application/octet-stream')
			doc.append('Content-length: %d' % len(p.stdout))
			doc.append('')
			doc.append(p.stdout.decode())
		else:
			doc.append('Content-type: text/html')
			doc.append('Status: 500 Server Error')
			doc.append('Retry-After: 60')
			doc.append('')
			doc.append(p.stderr.decode())
		
		print('\n'.join(doc))
		
