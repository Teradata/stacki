# $Id$
# 
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.1  2011/01/11 17:35:18  bruno
# dump the host public keys
#
#

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'host-key'
		
	def requires(self):
		return [ 'host' ]
		
	def run(self, args):
		self.owner.addText(self.owner.command('dump.host.key', []))
		

