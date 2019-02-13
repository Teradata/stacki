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

import os
import stack.commands
from stack.exception import CommandError


class command(stack.commands.create.command):
	MustBeRoot = 0


class Command(command):
	"""
	Create a RSA private/public key pair. These keys can be used to
	control the power for host and to open a console to VM. The private
	key will be stored in the specified by the 'key' parameter and the
	public key will be written to standard out.

	<param type='string' name='key'>
	The filename that will be used to store the private key.
	</param>

	<param type='boolean' name='passphrase'>
	Set this to 'no' if you want a passphraseless private key. The default
	is 'yes'.
	</param>
	"""

	def run(self, params, args):
		(key, p) = self.fillParams([
			('key', None, True),
			('passphrase', 'yes')
			])

		passphrase = self.str2bool(p)
		
		if os.path.exists(key):
			raise CommandError(self, "key file '%s' already exists" % key)

		#
		# generate the private key
		#
		cmd = 'openssl genrsa '
		if passphrase:
			cmd += '-des3 '
		cmd += '-out %s 1024' % key
		status = os.system(cmd)
		if status == 0:
			os.chmod(key, 0o400)

			#
			# output the public key
			#
			os.system('openssl rsa -in %s -pubout' % key)
		else:
			os.remove(key)

