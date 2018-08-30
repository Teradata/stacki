# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'volume'


	def run(self, args):

		if args  and 'volume' not in args:
			return

		document_prep = {'volume':[]}

		# if there is no data use an empty list as a placeholder.
		volume_data = self.owner.call('list.netapp.array.volume')
		if not volume_data:
			return document_prep
		volume_prep = []
		for volume in volume_data:
			volume_prep.append({
					'array':volume['array'],
					'volumegroup':volume['volumegroup'],
					'volumename':volume['volumename'],
					'size':volume['size'],
					'options':volume['options'],
					'hostgroup':volume['hostgroup'],
					'controllerid':volume['controllerid']
					})

		document_prep['volume'] = volume_prep


		return(document_prep)
