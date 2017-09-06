# @SI_Copyright@
# @SI_Copyright@

import os
from pprint import *
import stack.commands


class Plugin(stack.commands.Plugin):
	"SuSe Stuff"

	def provides(self):
		return 'sles'

	def requires(self):
		return ([ 'stacki' ])

	def run(self, attrs):

		if not 'os' in attrs or attrs['os'] != 'sles':
			return

		row = self.owner.call('report.host.storage.partition',
			[ attrs['hostname'] ])
		partition_output = row[0]['col-1']

		row = self.owner.call('report.host.storage.controller',
			[ attrs['hostname'] ])
		controller_output = row[0]['col-1']

		self.owner.addText('<stack:stacki><![CDATA[\n')

		self.owner.addText("""
#
# SLES
#
csv_partitions = %s

csv_controller = %s

"""
% (partition_output, controller_output))

		self.owner.addText(']]></stack:stacki>\n')

