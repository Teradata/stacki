# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands


class command(stack.commands.Command):
	MustBeRoot = 0

	def getSubnet(self, subnet, netmask):
		"""
		This Function returns a subnet with a
		CIDR netmask that is not a multiple of
		8. This means subnets smaller than /24 (25-32)
		will result in the correct subnet being
		backend for named.conf. It also needs to
		return a subnet on the octet boundary for
		netmasks that are in the 23..8 range. For
		more info read RFC2317
		"""
		s_list = list(map(int, subnet.split('.')))
		n_list = list(map(int, netmask.split('.')))
		
		net_list = []
		cidr = 0
		for i in range(0, 4):
			if n_list[i] == 0:
				break
			elif n_list[i] == 255:
				net_list.append(str(s_list[i]))
				cidr = cidr + 8
			else:
				b = n_list[i]
				s = 0
				while (b > 0):
					b = (b << 1 ) - 256
					s = s + 1
				s = cidr + s
		return net_list
