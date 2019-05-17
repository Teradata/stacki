# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin, stack.commands.list.command):

	def provides(self):
		return 'basic'

	def run(self, args):
		(hosts, expanded, hashit) = args

		keys      = [ ] 
		host_info = dict.fromkeys(hosts)
		for host in hosts:
			host_info[host] = []

		if expanded:
			# This is used by the MessageQ as a permanent handle on
			# Redis keys. This allows both the networking and names
			# of hosts to change and keeps the mq happy -- doesn't
			# break the status in 'list host'.
			keys.append('id')

		rows = self.graphql(query_string = """
		query nodes($expanded: Boolean!) {
		  nodes {
		    id: ID @include(if: $expanded)
		    name: Name
		    rack: Rack
		    rank: Rank
		    appliance {
		      name: Name
		    }
		    rank: Rank
		    box {
		      name: Name
		      os {
			name: Name
		      }
		    }
		    environment {
		      name: Name
		    }
		    os_action {
		      bootname {
			name: Name
		      }
		    }
		    install_action {
		      bootname {
			name: Name
		      }
		    }
		    comment: Comment
		  }
		}
		""", variables = {"expanded": expanded})

		for host in rows['nodes']:
			host_name = host['name']
			host_values = []
			host_values.append(host.get('rack'))
			host_values.append(host.get('rank'))
			host_values.append(host.get('appliance', {}).get('name'))
			host_values.append(host.get('box', {}).get('os', {}).get('name'))
			host_values.append(host.get('box', {}).get('name'))

			environment = host.get('environment')
			if environment:
				environment = environment.get('name')

			host_values.append(environment)
			host_values.append(host.get('os_action', {}).get('bootname', {}).get('name'))
			host_values.append(host.get('install_action', {}).get('bootname', {}).get('name'))
			host_info[host_name].extend(host_values)

		keys.extend(['rack', 'rank',
			     'appliance',
			     'os', 'box',
			     'environment',
			     'osaction', 'installaction'])

		return { 'keys' : keys, 'values': host_info }

