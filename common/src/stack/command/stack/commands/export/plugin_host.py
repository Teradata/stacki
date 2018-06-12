# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'host'


	def run(self, args):

		if args:
			if 'host' not in args:
				return

		document_prep = {'host':[]}

		#json.loads(Nonetype) fails, so first check that our 'stack list' command returned something.
		#if not, use an empty list as a placeholder.
		host_data = self.owner.command('list.host', [ 'output-format=json' ])
		if host_data:
			host_data = json.loads(host_data)		

			for host in host_data:
				hostname = host['host']
				interface_data = self.owner.command('list.host.interface', [ f'{hostname}', 'output-format=json' ])
				if interface_data:
					interface_data = json.loads(interface_data)
				interface_alias_data = self.owner.command('list.host.alias', [ f'{hostname}', 'output-format=json' ])
				if interface_alias_data:
					interface_alias_data = json.loads(interface_alias_data)
				else:
					interface_alias_data = []

				attr_data = self.owner.command('list.host.attr', [ f'{hostname}', 'output-format=json' ])
				if attr_data:
					attr_data = json.loads(attr_data)

				firewall_data = self.owner.command('list.host.firewall', [ f'{hostname}', 'output-format=json' ])
				if firewall_data:
					firewall_data = json.loads(firewall_data)

				route_data = self.owner.command('list.host.route', [ f'{hostname}', 'output-format=json' ])
				if route_data:
					route_data = json.loads(route_data)

				group_data = self.owner.command('list.host.group', [ f'{hostname}', 'output-format=json' ])
				if group_data:
					group_data = json.loads(group_data)

				partition_data = self.owner.command('list.storage.partition', [ f'{hostname}', 'output-format=json' ])
				if partition_data:
					partition_data = json.loads(partition_data)

				controller_data = self.owner.command('list.storage.controller', [ f'{hostname}', 'output-format=json' ])
				if controller_data:
					controller_data = json.loads(controller_data)
		


			for host in host_data:
				hostname = host['host']
			
				interface_prep = []
				for interface in interface_data:
					if interface['host'] == hostname:
						interface_prep.append({'name':interface['interface'], 'mac':interface['mac'], 'ip':interface['ip'], 'network':interface['network'], 'alias':interface_alias_data})
			
				attr_prep = []
				for attr in attr_data:
					if attr['host'] == hostname:
						if attr['scope'] == 'host':
							if attr['type'] == 'shadow':
								shadow = True
							else:
								shadow = False
							attr_prep.append({'name':attr['attr'], 'value':attr['value'], 'shadow':shadow})
		
				firewall_prep = []
				for rule in firewall_data:
					if rule['host'] == hostname:
						firewall_prep.append(rule)
	
				route_prep = []
				for route in route_data:
					if route['host'] == hostname:
						route_prep.append(route)

				group_prep = []
				for group in group_data:
					if group['host'] == hostname:
						
						groups = group['groups'].split()
						for item in groups:
							group_prep.append(item)

				partition_prep = []
				if partition_data:
					for partition in partition_data:
						if partition['name'] == hostname:
							partition_prep.append(partition)
			
				controller_prep = []
				if controller_data:
					for controller in controller_data:
						if controller['name'] == hostname:
							controller_prep.append(controller)
				


			document_prep['host'].append({'name':hostname, 'rack':host['rack'], 'rank':host['rank'], 'interface':interface_prep, 'attrs':attr_prep, 
									'firewall':firewall_prep, 'box':host['box'], 'appliance':host['appliance'], 'comment':host['comment'], 
									'metadata':'metadata', 'environment':host['environment'], 'osaction':host['osaction'], 'route':route_prep, 
									'group':group_prep, 'partition':partition_prep, 'controller':controller_prep})



		return(document_prep)

RollName = "stacki"
