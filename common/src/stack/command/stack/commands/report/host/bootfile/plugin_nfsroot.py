# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import shutil
import stack.commands


class Plugin(stack.commands.Plugin):
	"""
	Generate a PXE specific configuration file
	"""

	def provides(self):
		return 'pxe'

	def run(self, ha):

		for host in ha:
			if 'interfaces' not in ha[host]:
				continue
			if ha[host]['os'] != 'raspbian':
				continue

			nfsroot = {}
			for row in self.owner.call('list.nfsroot'):
				nfsroot[row['name']] = {'nfs'  : row['nfs'],
							'tftp' : row['tftp']}

			for interface in ha[host]['interfaces']:
				tftpdir = os.path.join(os.path.sep, 
						       'tftpboot', 
						       '-'.join(map(lambda x: x.lower(), interface['mac'].split(':'))))

				self.owner.addOutput(host, f'rm -rf {tftpdir}')
				if ha[host]['type'] == 'os' and ha[host]['nfsroot'] and ha[host]['kernel']:
					self.owner.addOutput(host, f'mkdir {tftpdir}')
					self.owner.addOutput(host, f'cd {tftpdir}')
					self.owner.addOutput(host, f'for x in ../{nfsroot[ha[host]["nfsroot"]]["tftp"]}/*; do ln -s $x; done')
					self.owner.addOutput(host, f'rm -f {tftpdir}/cmdline.txt')
					self.owner.addOutput(host, 
						f'<stack:file stack:name="{tftpdir}/cmdline.txt" stack:owner="root:apache" stack:perms="0664" stack:rcs="off"><![CDATA[')
					self.owner.addOutput(host,
						f'{ha[host]["args"]} {ha[host]["kernel"]}:/export/stack/roots/{nfsroot[ha[host]["nfsroot"]]["nfs"]},nfsvers=3')
					self.owner.addOutput(host, ']]>\n</stack:file>')
