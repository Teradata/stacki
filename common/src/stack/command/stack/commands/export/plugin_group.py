# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json
class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'group'


	def run(self,args):

		if args:
			if 'group' not in args:
				return

		document_prep = {'group':[]}

		#json.loads(Nonetype) fails, so first check that our 'stack list' command returned something.
		#if not, use an empty list as a placeholder.
		group_data = self.owner.command('list.group', [ 'output-format=json' ])
		if group_data:
			group_data = json.loads(group_data)
			group_prep = []
			for group in group_data:
				group_prep.append({'name':group['group']})

			document_prep['group'] = group_prep


		return(document_prep)

