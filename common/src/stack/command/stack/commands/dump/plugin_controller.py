# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'controller'


	def run(self, args):

		if args  and 'controller' not in args:
			return

		document_prep = {'controller':[]}

		# if there is no data use an empty list as a placeholder.
		controller_data = self.owner.call('list.netapp.array.controller')
		if not controller_data:
			return document_prep
		controller_prep = []
		for controller in controller_data:
			controller_prep.append({
					'array':controller['array'],
					'controller':controller['controller'],
					'mac':controller['mac'],
					'options':controller['options']
					})

		document_prep['controller'] = controller_prep


		return(document_prep)
