# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'volumegroup'


	def run(self, args):

		if args  and 'volumegroup' not in args:
			return

		document_prep = {'volumegroup':[]}

		# if there is no data use an empty list as a placeholder.
		volumegroup_data = self.owner.call('list.netapp.array.volumegroup')
		if not volumegroup_data:
			return document_prep
		volumegroup_prep = []
		for volumegroup in volumegroup_data:
			volumegroup_prep.append({
					'array':volumegroup['array'],
					'tray':volumegroup['tray'],
					'slot':volumegroup['slot'],
					'raidlevel':volumegroup['raidlevel'],
					'volumegroup':volumegroup['volumegroup'],
					'options':volumegroup['options']
					})

		document_prep['volumegroup'] = volumegroup_prep


		return(document_prep)
