# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'basic'

	def run(self, args):
		(hosts, expanded, _) = args

		info = dict.fromkeys(hosts)

		for id, name, rack, rank, appliance, box, image, nfsroot, environment, bno, bni in self.db.select(
			"""
			n.id, n.name, n.rack, n.rank, 
			a.name,
			b.name, i.name, r.name,
			e.name, 
			bno.name, bni.name from 
			nodes n 
			left join appliances a   on n.appliance     = a.id
			left join boxes b        on n.box           = b.id 
			left join images i       on n.image         = i.id
			left join nfsroots r     on n.nfsroot       = r.id
			left join environments e on n.environment   = e.id 
			left join bootnames bno  on n.osaction      = bno.id 
			left join bootnames bni  on n.installaction = bni.id
			"""):
			if name in info:
				info[name] = {'id': id,
					      'name': name,
					      'rack': rack,
					      'rank': rank,
					      'appliance': appliance,
					      'box': box,
					      'image': image,
					      'nfsroot': nfsroot,
					      'environment': environment,
					      'bno': bno,
					      'bni': bni}

				info[name]['os'] = self.db.getHostOS(name)

		# This is (and the above dict) is more work than it needs to
		# be, but we want to give flexibility at ordering the columns
		# because the addition of nfsroot and image is going to look
		# weird and we aren't sure how best to display it without
		# freaking people out.

		keys = []
		if expanded:
			# This is used by the MessageQ as a permanent handle on
			# Redis keys. This allows both the networking and names
			# of hosts to change and keeps the mq happy -- doesn't
			# break the status in 'list host'.
			keys.append('id')

		keys.extend(['rack', 'rank',
			     'appliance',
			     'os', 
			     'box',
			     'image',
			     'nfsroot',
			     'environment',
			     'osaction', 'installaction'])

		values = {}
		for host in hosts:
			v = []
			i = info[host]
			if expanded:
				v.append(i['id'])
			v.extend([i['rack'], i['rank'],
				  i['appliance'],
				  i['os'],
				  i['box'],
				  i['image'],
				  i['nfsroot'],
				  i['environment'],
				  i['bno'],
				  i['bni']])
			values[host] = v


		return { 'keys' : keys, 'values': values }

