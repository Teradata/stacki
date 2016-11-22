#
# @SI_COPYRIGHT@
# @SI_COPYRIGHT@
#

import os
import sys
import re
import stack.commands

class Implementation(stack.commands.Implementation):

	def run(self, args):
		host = args[0]

		self.owner.addOutput(host, '<file name="/etc/resolv.conf">')
		self.owner.outputResolv(host)
		self.owner.addOutput(host, '</file>')

