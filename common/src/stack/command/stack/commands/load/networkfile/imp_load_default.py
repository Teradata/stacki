# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

# check all this awesomeness here
# check if valid netmask/ip
# check if name exists and is correct
# if not private, check for default (later)

import stack.csv
import stack.commands
from ipaddress import IPv4Address, IPv4Network, IPv6Network, IPv6Address 
from stack.exception import CommandError


class Implementation(stack.commands.NetworkArgumentProcessor,
	stack.commands.Implementation):	

	"""
	Put network configuration into the database based on
	a comma-separated formatted file.
	"""
	def checkValidIP(self, name, keyname, key):
			if not key:
				msg = 'Hey! I need a valid %s for the "%s" network.' % (keyname, name)
				raise CommandError(self.owner, msg)
			else:
				key = u'%s' % key

				# Check that address is valid
			try:
				if IPv4Address(key):
					self.owner.networks[name][keyname] = key 
				elif IPv6Address(key):
					self.owner.networks[name][keyname] = key
			except:
				msg = 'Hey! I need a valid %s for the ' % keyname
				msg += '"%s" network.' % name
				raise CommandError(self.owner, msg)

	def checkValidNetwork(self, name, keyname, key):
			if not key:
				msg = 'Hey! I need a valid %s for the "%s" network.' % (keyname, name)
				raise CommandError(self.owner, msg)
			else:
				key = u'%s' % key

				# Check that address is valid
			try:
				if IPv4Network(key):
					self.owner.networks[name][keyname] = key 
				elif IPv6Network(key):
					self.owner.networks[name][keyname] = key
			except:
				msg = 'Hey! I need a valid %s for the ' % keyname
				msg += '"%s" network.' % name
				raise CommandError(self.owner, msg)

	def run(self, args):
		filename, = args

		# get current networks for comparison
		self.owner.current_networks = {}
		subnets = self.owner.call('list.network', ['output-format=text'])
		for i in subnets:
			self.owner.current_networks[i['network']] = i

		try:
			reader = stack.csv.reader(open(filename, encoding='ascii'))
			header = None
			line = 0

			for row in reader:
				line += 1

				if not header:
					header = row

					#
					# make checking the header easier
					#
					required = ['network', 'zone', 'address', 'mask']

					for i in range(0, len(row)):
						header[i] = header[i].lower()

						if header[i] in required:
							required.remove(header[i])

					if len(required) > 0:
						msg = 'the following required fields are not present in the input file: '
						msg += '"%s"' % ', '.join(required)	
						CommandError(self.owner, msg)

					continue

				name = None
				address = None
				mask = None
				mtu = None
				zone = None
				dns = None
				pxe = None
				gateway = None

				for i in range(0, len(row)):
					field = row[i]
					if not field:
						continue

					if header[i] == 'network':
						if field:
							name = field.lower()

					elif header[i] == 'address':
						if field:
							address = field

					elif header[i] == 'zone':
						if field:
							zone = field

					elif header[i] == 'mask':
						if field:
							mask = field

					elif header[i] == 'mtu':
						if field:
							mtu = field

					elif header[i] == 'dns':
						if field:
							dns = field

					elif header[i] == 'pxe':
						if field:
							pxe = field

					elif header[i] == 'gateway':
						if field:
							gateway = field

				self.owner.networks[name] = {}

				if not name:
					msg = 'Hey! I need a network name in line '
					msg += '%s' % line
					raise CommandError(self.owner, msg)
				else:
					self.owner.networks[name]['network'] = name 

				# Validated addresses and netmask.
				self.checkValidIP(name, 'address', address)
				self.checkValidNetwork(name, 'mask', mask)
				if gateway is not None:
					self.checkValidIP(name, 'gateway', gateway)

				# You have an address and a mask check if they're valid together.
				# You probably don't need this since a bad netmask and a bad
				# IP will both be caught.
				try:
					if IPv4Network(u"%s/%s" % (address, mask)):
						pass
					elif IPv6Network(u"%s/%s" % (address, mask)):
						pass
				except:
					msg = 'Hey! I need valid address/netmask for the '
					msg += '"%s" network.' % name
					raise CommandError(self.owner, msg)

				# I'm going to do myself a favor and clean the zone here.
				# Otherwise I have to check if it's None or False or some
				# other such boolean in the plugin file.
				if zone in [None, 'False', 'True']:
					self.owner.networks[name]['zone'] = ''
				else:
					self.owner.networks[name]['zone'] = zone
				# add all the rest that we don't care if you screwed up.
				if mtu:
					self.owner.networks[name]['mtu'] = mtu
				if not dns:
					self.owner.networks[name]['dns'] = False
				if not pxe:
					self.owner.networks[name]['pxe'] = False
		except UnicodeDecodeError:
			raise CommandError(self.owner, 'non-ascii character in file')

		# bail if there are apparent duplicates.
		if len(self.owner.networks.keys()) < line - 1:
			msg = 'I\'ve detected %s lines in the file but only ' \
				% (line - 1)
			msg += '%s networks. Do you have duplicates?' \
				% len(self.owner.networks.keys())
			raise CommandError(self.owner, msg)
