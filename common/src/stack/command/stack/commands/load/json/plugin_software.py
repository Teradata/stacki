# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import json

class Plugin(stack.commands.Plugin):
	
	def provides(self):
		return 'software'

	
	def run(self, args):
		
		#check if the user would like to import software data
		#if there are no args, assume the user would like to import everthing
		if args and 'software' not in args:
			return

		#self.owner.data contains the data from the json file defined in init
		#check if there is any software data before we go getting all kinds of key errors
		if 'software' in self.owner.data:
			import_data = self.owner.data['software']
		else:
			print('no software data in json file')
			return

		#check to make sure 'box' 'pallet' and 'cart' all exist first to avoid a key error
		if import_data['box']:
			for box in import_data['box']:
				box_name = box['name']
				os_name = box['os']
				try:
					self.owner.command('add.box', [ 
								f'{box_name}', 
								f'os={os_name}' ])
					print(f'success adding box {box}')
					self.owner.successes += 1

				except Exception as e:
					if 'exists' in str(e):
						print(f'warning importing box {box}: {e}')
						self.owner.warnings += 1
					else:
						print(f'error adding box {box}: {e}')
						self.owner.errors += 1


		if import_data['pallet']:
			for pallet in import_data['pallet']:
				pallet_dir =  pallet['url']
				if pallet_dir == None:
					#if we have no url to fetch the pallet from we cannot add it, so skip to the next one
					print(f'error adding pallet {pallet}: no url found')
					self.owner.errors += 1
					continue
				
				if pallet['urlauthUser'] and pallet['urlauthPass']:
					try:
						self.owner.command('add.pallet', [ pallet_dir, 
									f'username={pallet["urlauthUser"]}', 
									f'password={pallet["urlauthPass"]}' ])
						print(f'success adding pallet {pallet}')
						self.owner.successes += 1

					except Exception as e:
						if 'exists' in str(e):
							print(f'warning adding pallet {pallet}: {e}')
							self.owner.warnings += 1
						else:
							print(f'error adding pallet {pallet}: {e}')
							self.owner.errors += 1
				else:

					try:
						self.owner.command('add.pallet', [ pallet_dir ])
						print(f'success adding pallet {pallet}')
						self.owner.successes += 1

					except Exception as e:
						if 'exists' in str(e):
							print(f'warning adding pallet {pallet}: {e}')
							self.owner.warnings += 1
						else:
							print(f'error adding pallet {pallet}: {e}')
							self.owner.errors += 1


				#allow for multiple boxes or no boxes at all
				for box in pallet['boxes']:
					try:
						self.owner.command('enable.pallet', [ pallet['name'], 
									f'release={pallet["release"]}', 
									f'box={box}' ])
						print(f'success enabling {pallet} in {box}')
						self.owner.successes += 1

					except Exception as e:
						print(f'error enabling {pallet["name"]} in {box}: {e}')
						self.owner.errors += 1


		if import_data['cart']:
			for cart in import_data['cart']:
				cart_name = ['name']
				boxes = []
				for box in cart['boxes']:
					boxes.appned(box)
				try:
					self.owner.command('add.cart', [ cart_name ])
					print(f'success adding cart {cart}')
					self.owner.successes += 1

				except Exception as e:
					if 'exists' in str(e):
						print(f'warning importing cart {cart}: {e}')
						self.owner.warnings += 1
					else:
						print(f'error importing cart {cart}: {e}')
						self.owner.errors += 1

