# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from pprint import pformat
import stack.commands


class Plugin(stack.commands.Plugin):
	"Common <stacki></stacki> section"

	def provides(self):
		return 'stacki'

	def run(self, attrs):
		row = self.owner.call('report.host.storage.partition',
			[ attrs['hostname'] ])
		partition_output = row[0]['col-1']

		row = self.owner.call('report.host.storage.controller',
			[ attrs['hostname'] ])
		controller_output = row[0]['col-1']

		self.owner.addText('<stack:stacki><![CDATA[\n')
		self.owner.addText('attributes = %s\n' % pformat(attrs))
		self.owner.addText("""
#
# Generic For All OSes
#
csv_partitions = %s

csv_controller = %s

"""
% (partition_output, controller_output))

		self.owner.addText(']]></stack:stacki>\n')

