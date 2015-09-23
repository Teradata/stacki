# @SI_Copyright@
#                             www.stacki.com
#                                  v2.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#

# check all this shit here
# check if valid netmask/ip
# check if name exists and is correct
# if not private, check for default (later)
import csv
import re
import sys
import stack.commands
import ast
from ipaddress import IPv4Address, IPv4Network, IPv6Network, IPv6Address 
from stack.exception import *

class Implementation(stack.commands.NetworkArgumentProcessor,
	stack.commands.Implementation):	

	"""
	Put network configuration into the database based on
	a comma-separated formatted file.
	"""
	def checkValidIP(self,name,keyname,key):
			if not key:
				msg = 'Hey! I need a valid %s for the "%s" network.' % (keyname,name)
				raise CommandError(self, msg)
			else:
				key = u'%s' % key

				# Check that address is valid
			try:
				if IPv4Address(key):
					self.owner.networks[name][keyname] = key 
				elif IPv6Address(gateway):
					self.owner.networks[name][keyname] = key
			except:
				msg = 'Hey! I need a valid %s for the ' % keyname
				msg += '"%s" network.' % name
				raise CommandError(self, msg)
	def checkValidNetwork(self,name,keyname,key):
			if not key:
				msg = 'Hey! I need a valid %s for the "%s" network.' % (keyname,name)
				raise CommandError(self, msg)
			else:
				key = u'%s' % key

				# Check that address is valid
			try:
				if IPv4Network(key):
					self.owner.networks[name][keyname] = key 
				elif IPv6Network(gateway):
					self.owner.networks[name][keyname] = key
			except:
				msg = 'Hey! I need a valid %s for the ' % keyname
				msg += '"%s" network.' % name
				raise CommandError(self, msg)

	def run(self, args):
		filename, = args

		# get current networks for comparison
		self.owner.current_networks = {}
                subnets = self.owner.call('list.network', ['output-format=text'])
		for i in subnets:
			self.owner.current_networks[i['network']] = i

		reader = csv.reader(open(filename, 'rU'))
		header = None
		line = 0

		for row in reader:
			line += 1

                        # Ignore empty rows in the csv which happens
                        # frequently with excel
                        
			empty = True
                        for cell in row:
                                if cell.strip():
                                        empty = False
                        if empty:
                                continue

			if not header:
				header = row

				#
				# make checking the header easier
				#
				required = ['NETWORK', 'ZONE', 'ADDRESS', 'MASK','GATEWAY', 'MTU', 'DNS','PXE']

				for i in range(0, len(row)):
					header[i] = header[i].strip().lower()

					if header[i] in required:
						required.remove(header[i])

				if len(required) > 0:
					msg = 'the following required fields are not present in the input file: '
					msg += '"%s"' % ', '.join(required)	
					CommandError(self, msg)

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
				field = row[i].strip()
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
				raise CommandError(self, msg)
			else:
				self.owner.networks[name]['network'] = name 

			# Validated addresses and netmask.
			self.checkValidIP(name,'address',address)
			self.checkValidNetwork(name,'mask',mask)
			self.checkValidIP(name,'gateway',gateway)

			# You have an address and a mask check if they're valid together.
			# You probably don't need this since a bad netmask and a bad
			# IP will both be caught.
			try:
				if IPv4Network(u"%s/%s" % (address,mask), strict=False):
					pass	
				elif IPv6Network(u"%s/%s" % (address,mask), strict=False):
					pass	
			except:
				msg = 'Hey! I need valid address/netmask for the '
				msg += '"%s" network.' % name
				raise CommandError(self, msg)

			# I'm going to do myself a favor and clean the zone here.
			# Otherwise I have to check if it's None or False or some
			# other such boolean in the plugin file.
			if zone in [None, 'False', 'True']:
				self.owner.networks[name]['zone'] = ''
			else:
				self.owner.networks[name]['zone'] = zone
			# add all the rest that we don't care if you screwed up.
			self.owner.networks[name]['mtu'] = mtu
			self.owner.networks[name]['dns'] = dns
			self.owner.networks[name]['pxe'] = pxe

		# bail if there are apparent duplicates.
		if len(self.owner.networks.keys()) < line - 1:
			msg = 'I''ve detected %s lines in the file but only ' \
				% (line - 1)
			msg += '%s networks. Do you have duplicates?' \
				% len(self.owner.networks.keys())
			raise CommandError(self, msg)

		# bail if 'private' is not defined			
		if 'private' not in self.owner.networks.keys() and \
			'private' not in self.owner.current_networks.keys():
			msg = '"private" network not found'
			raise CommandError(self, msg)
