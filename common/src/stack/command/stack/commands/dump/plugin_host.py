# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'host'


	def run(self, args):

		if args and 'host' not in args:
			return

		document_prep = {'host':[]}

		# if there is no data use an empty list as a placeholder.
		host_data = self.owner.call('list.host')
		if not host_data:
			return document_prep

		# since list host attr is relatively expensive, call it once for all hosts up here
		grouped_hosts = {}
		for line in self.owner.call('list.host.attr'):
			if line['host'] in grouped_hosts:
				grouped_hosts[line['host']].append(line)
			else:
				grouped_hosts[line['host']] = [line]

		for host in host_data:
			hostname = host['host']
			interface_data = self.owner.call('list.host.interface', [ hostname ])
			if not interface_data:
				interface_data = []
			interface_prep = []
			for interface in interface_data:
				# grab the alias data for this interface
				interface_alias_data = self.owner.call('list.host.alias', [
											hostname,
											f'interface={interface["interface"]}'
				])
				if not interface_alias_data:
					interface_alias_data = []

				if interface['host'] == hostname:
					interface_prep.append({
							'interface':interface['interface'],
							'default':interface['default'],
							'mac':interface['mac'],
							'ip':interface['ip'],
							'network':interface['network'],
							'name':interface['name'],
							'module':interface['module'],
							'vlan':interface['vlan'],
							'options':interface['options'],
							'channel':interface['channel'],
							'alias':interface_alias_data
					})
			attr_data = grouped_hosts[hostname]
			if not attr_data:
				attr_data = []
			attr_prep = []
			metadata = None
			for attr in attr_data:
				if attr['host'] == hostname:
					if attr['scope'] == 'host':
						# metadata is stored as an attr and we want to pull it to the side
						# once we have it we dont want to keep it with the rest of the attrs
						if attr['attr'] == 'metadata':
							metadata = attr['value']
							continue

						if attr['type'] == 'shadow':
							shadow = True
						else:
							shadow = False
						attr_prep.append({
							'name':attr['attr'],
							'value':attr['value'],
							'shadow':shadow
							})

			firewall_data = self.owner.call('list.host.firewall', [ hostname ])
			if not firewall_data:
				firewall_data = []
			firewall_prep = []
			for rule in firewall_data:
				if rule['host'] == hostname and rule['source'] == 'H':
					firewall_prep.append(rule)


			route_data = self.owner.call('list.host.route', [ hostname ])
			if not route_data:
				route_data = []
			route_prep = []
			for route in route_data:
				if route['host'] == hostname and route['source'] == 'H':
					route_prep.append(route)


			group_data = self.owner.call('list.host.group', [ hostname ])
			if not group_data:
				group_data = []
			group_prep = []
			for group in group_data:
				if group['host'] == hostname:

					groups = group['groups'].split()
					for item in groups:
						group_prep.append(item)


			partition_data = self.owner.call('list.storage.partition', [ hostname ])
			if not partition_data:
				partition_data = []
			partition_prep = []
			if partition_data:
				for partition in partition_data:
					if partition['scope'] == hostname:
						partition_prep.append(partition)


			controller_data = self.owner.call('list.storage.controller', [ hostname ])
			if not controller_data:
				controller_data = []

			# find the longname of the host's appliance with list appliance
			appliance_data = self.owner.call('list.appliance', [ host['appliance'] ])
			longname = appliance_data[0]['long name']


			document_prep['host'].append({
						'name':hostname,
						'rack':host['rack'],
						'rank':host['rank'],
						'interface':interface_prep,
						'attrs':attr_prep,
						'firewall':firewall_prep,
						'box':host['box'],
						'appliance':host['appliance'],
						'appliancelongname':longname,
						'comment':host['comment'],
						'metadata':metadata,
						'environment':host['environment'],
						'osaction':host['osaction'],
						'installaction':host['installaction'],
						'route':route_prep,
						'group':group_prep,
						'partition':partition_prep,
						'controller':controller_data
						})
		return(document_prep)
