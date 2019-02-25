# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack
import stack.commands
import json
from collections import OrderedDict

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'software'


	def run(self, args):
		box    = json.loads(self.owner.command('dump.box'),
				    object_pairs_hook=OrderedDict)
		cart   = json.loads(self.owner.command('dump.cart'),
				    object_pairs_hook=OrderedDict)
		pallet = json.loads(self.owner.command('dump.pallet'),
				    object_pairs_hook=OrderedDict)

		return json.dumps(OrderedDict(
			version  = stack.version,
			software = OrderedDict(
				box    = box['software']['box'],
				cart   = cart['software']['cart'],
				pallet = pallet['software']['pallet'])), indent=8)

