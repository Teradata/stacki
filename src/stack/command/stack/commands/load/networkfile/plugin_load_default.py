# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@

import stack.commands
from stack.exception import *

class Plugin(stack.commands.NetworkArgumentProcessor, stack.commands.Plugin):

	def provides(self):
		return 'default'

	def removeNetwork(self, networks):
		setlist = []
		for k in networks.keys():
			if k in self.getNetworkNames():
				try:
					self.owner.call('remove.network', 
					[ '%s' % k])
				except:
					setlist.append(k)
		return setlist

	def returnDiffs(self,network):
		for k,v in self.networks[network].iteritems():
			self.networks[network][k] = str(v or '')

		for k,v in self.current_networks[network].iteritems():
			self.current_networks[network][k] = str(v or '')
		a = set(self.current_networks[network].items())
		b = set(self.networks[network].items())
		c = b - a
		return c

	def run(self, args):
		self.networks,self.current_networks = args
		netsforset = self.removeNetwork(self.networks)
		for network in self.networks:
			if network in netsforset:
				# get the diffs between what is and what is to be
				diffs = self.returnDiffs(network)
				for diff in diffs:
					setnetargs = [network, str('%s=%s' \
							% (diff[0], diff[1]))]
					self.owner.call('set.network.%s' % 
							diff[0], setnetargs)

			else:
				addnetargs = [network]
				for k,v in self.networks[network].items():
					addnetargs.append("%s=%s" % (k,v))
				self.owner.call('add.network', addnetargs)
