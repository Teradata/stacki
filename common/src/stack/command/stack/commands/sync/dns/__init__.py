# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@


import os
import string
import stack.file
import stack.commands


class Command(stack.commands.sync.command):
	"""
	Rebuild the DNS configuration files, then restart named.

	<example cmd='sync dns'>
	Rebuild the DNS configuration files, then restart named.
	</example>
	"""

	def getNetwork(self):
		"Returns the network address of this cluster"

		self.db.execute("""select subnet from subnets where
			name = 'private'""")
		network, = self.db.fetchone()
		
		return network


	def getNetmask(self, net):
		"Determines the network mask of this cluster. Returns"
		"a CIDR value i, 0<=i<=32. Handles only IPv4 addresses."

		mask = 32
		Net = string.split(net, ".")
		for i in Net:
			for j in range(0, 8):
				if int(i) & 2**j:
					break
				mask -= 1

		return mask


	def getSubnets(self):
		list = []

		network = self.getNetwork()
		netmask = self.getNetmask()

		w = string.split(network, '.')
		work = []
		for i in w:
			work.append(int(i))

		for i in range(0, 4):
			if netmask < 8:
				break
			else:
				netmask -= 8

		octet_index = i
		octet_value = work[i]

		if netmask == 0:
			#
			# no subnetting
			#
			subnet = []

			for j in range(0, octet_index):
				subnet.append('%d' % (work[j]))

			list = [ subnet ]
		else:
			for i in range(0, 2**(8 - netmask)):
				work[octet_index] = octet_value + i
				if work[octet_index] > 254:
					break

				subnet = []
				for j in range(0, octet_index + 1):
					subnet.append('%d' % (work[j]))

				if list == []:
					list = [ subnet ]
				else:
					list.append(subnet)

		return list


	def run(self, params, args):

		self.notify('Sync DNS\n')

		self.runPlugins()
		os.system('/sbin/service named reload > /dev/null 2>&1')
