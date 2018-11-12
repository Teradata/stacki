# @SI_Copyright@
# @SI_Copyright@

import os
from pprint import *
import stack.commands
import subprocess


class Plugin(stack.commands.Plugin):
	"Ubuntu Stuff"

	def provides(self):
		return 'ubuntu'

        def requires(self):
                return ([ 'stacki' ])

	def run(self, attrs):

                if not attrs.has_key('os') or attrs['os'] != 'ubuntu':
                        return

		row = self.owner.call('report.host.storage.partition',
			[ attrs['hostname'] ])
		partition_output = row[0]['col-1']

		row = self.owner.call('report.host.storage.controller',
			[ attrs['hostname'] ])
		controller_output = row[0]['col-1']


		row = self.owner.call('list.network')
#		#$network_output = for r in row['col-1']
		network_output = row
#
		row = self.owner.call('list.host.interface',
			[ attrs['hostname'] ])
		interface_output = row

		ssh_keys = {}	
		key_type = [ 'RSA', 'ECDSA', 'ED25519' ]
		for k in key_type:
			cmd = '/opt/stack/sbin/read-ssh-private-key %s' % k
			p = subprocess.Popen(cmd,stdout=subprocess.PIPE,
					stderr=subprocess.PIPE,shell=True)
			o,e = p.communicate()
			ssh_keys['%s_key' % k.lower()] = o

			cmd = 'cat /etc/ssh/ssh_host_%s_key.pub' % k.lower()
			p = subprocess.Popen(cmd,stdout=subprocess.PIPE,
					stderr=subprocess.PIPE,shell=True)
			o,e = p.communicate()
			ssh_keys['%s_key.pub' % k.lower()] = o
		
		cmd = 'cat /root/.ssh/id_rsa.pub'
		p = subprocess.Popen(cmd,stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,shell=True)
		o,e = p.communicate()
		ssh_keys['authorized_key'] = o
        	self.owner.addText('<stack:stacki><![CDATA[\n')

                self.owner.addText("""
#
# Ubuntu
#
csv_partitions = %s

csv_controller = %s

interfaces = %s

networks = %s

ssh_keys = %s

"""
% (partition_output, controller_output, interface_output, network_output, ssh_keys))

                self.owner.addText(']]></stack:stacki>\n')
