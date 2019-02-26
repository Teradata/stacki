# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import spwd
import subprocess
import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'unix'


	def run(self, args):
		if len(args) != 2:
			return

		old_password = args[0]
		new_password = args[1]

		#
		# use the system to change the password
		#
		self._exec('/usr/sbin/chpasswd', input=f'root:{new_password}')

		#
		# get the new crypted password
		#
		shadow_info = spwd.getspnam('root')

		if shadow_info:
			newpw = shadow_info.sp_pwd
			
			#
			# store it in the database
			# 
			self.owner.command('set.attr',
				[ 'attr=Kickstart_PrivateRootPassword', 
				  'value=%s' % newpw ] )
		else:
			print('Could not read the new password for root')

