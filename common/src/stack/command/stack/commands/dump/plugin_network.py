# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'network'


	def run(self, args):

		if args  and 'network' not in args:
			return

		document_prep = {'network':[]}

		# if there is no data use an empty list as a placeholder.
		network_data = self.owner.call('list.network')
		if not network_data:
			return document_prep
		network_prep = []
		for network in network_data:
			network_prep.append({
					'name':network['network'],
					'address':network['address'],
					'gateway':network['gateway'],
					'netmask':network['mask'],
					'dns':network['dns'],
					'pxe':network['pxe'],
					'mtu':network['mtu'],
					'zone':network['zone'],
					})

		document_prep['network'] = network_prep


		return(document_prep)
