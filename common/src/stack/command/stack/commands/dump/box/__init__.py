# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack
import stack.commands
from collections import OrderedDict


class Command(stack.commands.dump.command):

	def run(self, params, args):

		boxes = {}
		for row in self.call('list.box'):
			boxes[row['name']] = {'os'      : row['os'],
					      'carts'   : [],
					      'pallets' : []}

		for row in self.call('list.cart'):
			for box in row.get('boxes', '').split():
				boxes[box]['carts'].append(row['name'])

		for row in self.call('list.pallet'):
			for box in row.get('boxes', '').split():
				boxes[box]['pallets'].append(OrderedDict(
					name    = row['name'],
					version = row['version'],
					release = row['release'],
					arch    = row['arch'],
					os      = row['os']))

		dump = []
		for box in boxes:
			dump.append(OrderedDict(name   = box,
						os     = boxes[box]['os'],
						cart   = boxes[box]['carts'],
						pallet = boxes[box]['pallets']))

		self.addText(self.dumps(OrderedDict(version  = stack.version,
						    software = {'box' : dump})))

