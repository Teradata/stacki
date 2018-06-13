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
		if args:
			if 'software' not in args:
				return


		#self.owner.data contains the data from the json file defined in init
		for item in self.owner.data:
			if item == 'software':
				import_data = self.owner.data[item]
			else:
				print('error no software data in json file')
				return

		#check to make sure 'box' 'pallet' and 'cart' all exist first to avoid a key error
		if import_data['box']:
			for box in import_data['box']:
				box_name = box['name']
				os_name = box['os']
				#TODO: make a more specific try catch
				try:
					self.owner.command('add.box', [ f'{box_name}', f'os={os_name}' ])
				except:
					print(f'error importing box {box}')	

		if import_data['pallet']:
			for pallet in import_data['pallet']:
				pallet_dir =  pallet['url']
				pallet_name = pallet['name']
				pallet_version = pallet['version']
				pallet_release = pallet['release']
				boxes = []
				for box in pallet['boxes']:
					boxes.append(box)
				try:
					self.owner.command('add.pallet', [ pallet_dir, f'name={pallet_name}', f'release={pallet_release}', f'version={pallet_version}'])
				except:
					print(f'error importing pallet {pallet}')
			

		if import_data['cart']:
			for cart in import_data['cart']:
				cart_name = ['name']
				boxes = []
				for box in cart['boxes']:
					boxes.appned(box)
				try:
					self.command.run('add.cart', [ cart_name ])
				except:
					print(f'error importing cart {cart}')


