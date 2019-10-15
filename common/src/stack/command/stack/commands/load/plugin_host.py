# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'host'

	def requires(self):
		return [ 'software', 'network', 'appliance', 'bootaction', 'environment' ]

	def run(self, section):

		self.owner.set_scope('host')

		for h in section:
			host   = h.get('name')
			params = {'rack'         : h.get('rack'),
				  'rank'         : h.get('rank'),
				  'appliance'    : h.get('appliance'),
				  'box'          : h.get('box'),
				  'environment'  : h.get('environment'),
				  'osaction'     : h.get('osaction'),
				  'installaction': h.get('installaction'),
				  'comment'      : h.get('comment')}

			self.owner.stack('add.host', host, **params)

			metadata = h.get('metadata')
			if metadata:
				self.owner.stack('set.host.metadata',
						 host, [f'metadata={metadata}'])

			# group

			for i in h.get('interface', []):
				params    = {'interface': i.get('interface'),
					     'default'  : i.get('default'),
					     'network'  : i.get('network'),
					     'mac'      : i.get('mac'),
					     'ip'       : i.get('ip'),
					     'name'     : i.get('name'),
					     'module'   : i.get('module'),
					     'vlan'     : i.get('vlan'),
					     'options'  : i.get('options'),
					     'channel'  : i.get('channel')}

				self.owner.stack('add.host.interface', host, **params)

				for a in i.get('alias', []):
					params = {'interface': i.get('interface'),
						  'alias'    : a}
					self.owner.stack('add.host.interface.alias', host, **params)

			self.owner.load_attr(h.get('attr'), host)
			self.owner.load_controller(h.get('controller'), host)
			self.owner.load_partition(h.get('partition'), host)
			self.owner.load_firewall(h.get('firewall'), host)
			self.owner.load_route(h.get('route'), host)
