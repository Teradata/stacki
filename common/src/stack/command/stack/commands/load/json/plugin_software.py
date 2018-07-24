# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json
from stack.exception import CommandError
import logging

class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'software'


	def run(self, args):
		# Start a logger
#		log = logging.getLogger("stack-ws")

		# check if the user would like to import software data
		# if there are no args, assume the user would like to import everthing
		if args and 'software' not in args:
			return

		# self.owner.data contains the data from the json file defined in init
		# check if there is any software data before we go getting all kinds of key errors
		if 'software' in self.owner.data:
			import_data = self.owner.data['software']
		else:
			self.owner.log.info('no software data in json file')
			return

		# check to make sure 'box' 'pallet' and 'cart' all exist first to avoid a key error
		if import_data['box']:
			for box in import_data['box']:
				try:
					self.owner.command('add.box', [
								f'{box["name"]}',
								f'os={box["os"]}'
					])
					self._logger.info(f'success adding box {box["name"]}')
#					self.owner.log.info(f'success adding box {box["name"]}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning importing box {box["name"]}: {e}')
						self.owner.warnings += 1
					else:
						self.owner.log.info(f'error adding box {box["name"]}: {e}')
						self.owner.errors += 1


		if import_data['pallet']:
			for pallet in import_data['pallet']:
				pallet_dir =  pallet['url']
				if pallet_dir == None:
					# if we have no url to fetch the pallet from we cannot add it
					raise CommandError(self, f'error adding pallet {pallet["name"]} {pallet["version"]}: no url found')
					self.owner.errors += 1

					# the following code is now unreachable, does it have any value?

					# in the rare case that this pallet has no url but also currently exists in the database
					# we need to check to see if it needs to be added to any boxes
#					if not pallet['boxes']:
#						continue
#					pallet_data = self.owner.command('list.pallet', [ 'output-format=json', 'expanded=true' ])
#					if pallet_data:
#						pallet_data = json.loads(pallet_data)
#						for item in pallet_data:
#							if pallet['name'] == item['name']:
#								# we have now deduced that the pallet both is currently in the database and that it has boxes that it needs to be added to
#								for box in pallet['boxes']:
#									try:
#										self.owner.command('enable.pallet', [ pallet['name'],
#												f'release={pallet["release"]}',
#												f'box={box}' ])
#										self.owner.log.info(f'success enabling {pallet} in {box}')
#										self.owner.successes += 1
#
#									except CommandError as e:
#										self.owner.log.info(f'error enabling {pallet["name"]} in {box}: {e}')
#										self.owner.errors += 1
#						# we have finished with this pallet
#						continue


				try:
					parameters = [pallet_dir]
					if pallet['urlauthUser'] and pallet['urlauthPass']:
						parameters.append(f'username={pallet["urlauthUser"]}')
						parameters.append(f'password={pallet["urlauthPass"]}')
					self.owner.command('add.pallet', parameters)

					self.owner.log.info(f'success adding pallet {pallet["name"]} {pallet["version"]}')
					self.owner.successes += 1

				except CommandError as e:
					if 'exists' in str(e):
						self.owner.log.info(f'warning adding pallet {pallet}: {e}')
						self.owner.warnings += 1
					else:
						raise CommandError(self, f'error adding pallet {pallet["name"]} {pallet["version"]}: {e}')


				# allow for multiple boxes or no boxes at all
				for box in pallet['boxes']:
					try:
						self.owner.command('enable.pallet', [
										pallet['name'],
										f'release={pallet["release"]}',
										f'box={box}'
										])
						self.owner.log.info(f'success enabling {pallet["name"]} {pallet["version"]} in {box}')
						self.owner.successes += 1

					except CommandError as e:
						self.owner.log.info(f'error enabling {pallet["name"]}, {pallet["version"]} in {box}: {e}')
						self.owner.errors += 1


		if import_data['cart']:
			for cart in import_data['cart']:
				cart_name = ['name']
				boxes = []
				for box in cart['boxes']:
					boxes.append(box)

				# if the cart has a url then attempt to reach out and get it
				if cart['url']:
					parameters = [ cart['url'] ]
					# if the url starts with a / then we know that it is a local file
					# local carts need to be added with the file= parameter
					if cart['url'].startswith('/'):
						self.owner.command('add.cart', [ f'file={cart["url"]}' ])
						continue
					# check if the file is local or not
					if cart['urlauthUser']:
						parameters.append(f'username={cart["urlauthUser"]}')
					if cart['urlauthPass']:
						parameters.append(f'password={cart["urlauthPass"]}')
					self.owner.command('add.cart', parameters)

				else:

					try:
						self.owner.command('add.cart', [ cart['name'] ])
						self.owner.log.info(f'success adding cart {cart}')
						self.owner.successes += 1

					except CommandError as e:
						if 'exists' in str(e):
							self.owner.log.info(f'warning importing cart {cart}: {e}')
							self.owner.warnings += 1
						else:
							self.owner.log.info(f'error importing cart {cart}: {e}')
							self.owner.errors += 1

