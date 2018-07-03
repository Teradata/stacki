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
import json

class Command(stack.commands.Command):
	"""
	Export data into a single json document
	"""
	def run(self,params, args):
		#runPlugins() returns a list of tuples where tuple[0] is the plugin name and
		#tuple[1] is the return value
		#each plugin examins 'args' to determine if it runs or not
		data = self.runPlugins(args)
		document_prep = {}
		for plugin in data:
			document_prep.update(plugin[1])

		self.beginOutput()
		self.addOutput(None,json.dumps(document_prep))
		self.endOutput(trimOwner=True)


