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


class Command(stack.commands.report.command):
	"""
	Output the version of Stacki.

	<example cmd='report version'>
	Output the current Stacki version.
	</example>
	"""

	def run(self, params, args):
		self.beginOutput()
		self.addOutput('stacki', stack.version)
		self.endOutput(header=['layer', 'version'], 
			       trimOwner=True,
			       trimHeader=True)

