#! /opt/stack/bin/python3
#
# Using a combination of AWS user-data and data from the Frontend decide what
# to do on next boot.
#
# The primary design goal is to keep this script self-contained to minimize the
# dependencies added to the installation AMI.
#
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import sys
import os
import subprocess
import json
import time
import urllib.error
from urllib.request import urlopen


class InstanceInfo:
	"""
	Simple object to read and hold the instance information. This
	gets sent to the Frontend as part of the registration request.
	"""

	def __init__(self):
		self.user_data = self.__lookup('user-data')
		self.ami       = self.__lookup('meta-data/ami-id')
		self.zone      = self.__lookup('meta-data/placement/availability-zone')
		self.instance  = self.__lookup('meta-data/instance-id')
		self.hostname  = self.__lookup('meta-data/hostname')
		self.ip	       = self.__lookup('meta-data/local-ipv4')
		self.mac       = self.__lookup('meta-data/mac')
		self.sshkey    = self.__lookup('meta-data/public-keys/0/openssh-key')

	def __lookup(self, path):
		print('Query %s' % path)
		done = False
		while not done:
			try:
				response = urlopen('http://169.254.169.254/latest/%s' % path)
				done	 = True
			except urllib.error.HTTPError:
				print('retry')
				time.sleep(5)
		value = response.read().decode()
		print('\t%s' % value)
		return value


class BootInstructions:
	"""
	Simple object to hold the parse()ed client boot
	instructions.
	"""

	def __init__(self):
		self.master	= None
		self.hostname	= None
		self.appliance	= 'backend'
		self.box	= 'default'
		self.boot	= 'os'
		self.reboot	= False
		self.grub	= None
		self.grub2	= None
		self.images_url = None
		self.kernel	= None
		self.ramdisk	= None

	def parse(self, document):
		"""
		Loads a new BootInstructions JSON document into the
		object. These instructions come from either the
		instance's user-data or from the response to a
		registration request.
		"""

		instructions = json.loads(document)

		for name in [ 'master',
			      'hostname',
			      'appliance',
			      'box',
			      'boot',
			      'reboot',
			      'grub',
			      'grub2',
			      'images_url',
			      'kernel',
			      'ramdisk' ]:
			if name in instructions:
				exec('self.%s = """%s"""' % (name, instructions[name]))


def Download(url, dst):
	print('Download %s -> %s' % (url, dst))
	p = subprocess.Popen(['/usr/bin/curl', url],
			     stdout=subprocess.PIPE,
			     stderr=subprocess.PIPE)
	o, e = p.communicate()
	out = open(dst, 'wb')
	out.write(o)
	out.close()


# Grab the instance information and first pass of the boot instructions from
# the instance's user-data.

info	     = InstanceInfo()
instructions = BootInstructions()

instructions.parse(info.user_data)

if not instructions.master:
	print('ERROR - user-data has no defined "master"')
	sys.exit(-1)

if instructions.hostname:
	hostname = instructions.hostname.split('.')[0]
else:
	hostname = info.hostname.split('.')[0]

args = [ ]
args.append('hostname=%s'  % hostname)
args.append('appliance=%s' % instructions.appliance)
args.append('box=%s'	   % instructions.box)
args.append('ip=%s'	   % info.ip)
args.append('mac=%s'	   % info.mac)
args.append('instance=%s'  % info.instance)
args.append('ami=%s'	   % info.ami)
args.append('zone=%s'	   % info.zone)
p = subprocess.Popen(['/usr/bin/curl', '-s',
		      '--local-port', '1-100',
		      '--insecure',
		      'https://%s/install/sbin/register.cgi?%s' % (instructions.master, '&'.join(args))],
		     stdout=subprocess.PIPE,
		     stderr=subprocess.PIPE)
o, e = p.communicate()
instructions.parse(o.decode())

if instructions.boot == 'install':
	if instructions.kernel:
		Download(os.path.join(instructions.images_url, instructions.kernel), 
			 os.path.join(os.sep, 'boot', instructions.kernel))

	if instructions.ramdisk:
		Download(os.path.join(instructions.images_url, instructions.ramdisk), 
			 os.path.join(os.sep, 'boot', instructions.ramdisk))


	grubpath  = os.path.join(os.sep, 'etc', 'grub.conf')
	grub2path = os.path.join(os.sep, 'etc', 'grub.d', '40_custom')
	if os.path.exists(grub2path):
		print('\nWrite Grub2')
		for line in instructions.grub2.split('\n'):
			print('\t%s' % line)
		with open(grub2path, 'a') as out:
			out.write(instructions.grub2)
		with open(os.path.join(os.sep, 'etc', 'default', 'grub'), 'a') as out:
			out.write('GRUB_DEFAULT="stacki install"\n')
		os.system('grub2-mkconfig --output=/boot/grub2/grub.cfg')
	else:
		print('\nWrite Grub')
		for line in instructions.grub.split('\n'):
			print('\t%s' % line)
		with open(grubpath, 'w') as out:
			out.write(instructions.grub)

if instructions.reboot == "True":
	print('rebooting...')
	os.system('/sbin/init 6')


