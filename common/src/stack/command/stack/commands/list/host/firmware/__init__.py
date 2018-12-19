# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
import os
import re

class command(stack.commands.HostArgumentProcessor,
	stack.commands.list.command):
	pass
	

class Command(command):
	"""
	List the hosts, and their corresponding available and installed firmwares.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='list firmware backend-0-0'>
	List info for backend-0-0.
	</example>

	<example cmd='list firmware'>
	List info for all known hosts.
	</example>

	"""

	def run(self, params, args):
	    
		(order, expanded, hashit) = self.fillParams([
			('order',    'asc'), 
			('expanded', False),
			('hash',     False) 
		])
		
		hosts    = self.getHostnames(args, order=order)
		expanded = self.str2bool(expanded)
		hashit   = self.str2bool(hashit)
	    
		header = [ 'host' ]
		values = { }
		for host in hosts:
			values[host] = [ ]
			
		for (provides, result) in self.runPlugins((hosts, expanded, hashit)):
			header.extend(result['keys'])
			for h, v in result['values'].items():
				values[h].extend(v)

		self.beginOutput()
		for host in hosts:
			self.addOutput(host, values[host])
		self.endOutput(header=header, trimOwner=False)


def getFirmwarePath():
	return '/export/stack/firmware/'


def getAvailableVersion(appliance, make, model):
	if not make or make == 'None':
		make = ""
	if not model or make == 'None':
		model = ""
	if not os.path.exists(os.path.join(getFirmwarePath(), appliance, make, model)):
		return None
	files = os.listdir(os.path.join(getFirmwarePath(), appliance, make, model))
	if len(files) == 0:
		return None
	files = [extractVersionNumber(os.path.splitext(f)[0]) for f in files]
	latest_version = files[0]
	for i in range(1, len(files)):
		if compareVersion(files[i], latest_version) > 0:
			latest_version = files[i]
	return latest_version


def extractVersionNumber(text):
	if not text:
		return None
	pattern = r'(\d+\.)+(\d+)'
	extraction = re.search(pattern, text)
	return extraction.group()


def compareVersion(version1, version2):
	versions1 = [int(v) for v in version1.split(".")]
	versions2 = [int(v) for v in version2.split(".")]
	for i in range(max(len(versions1),len(versions2))):
		v1 = versions1[i] if i < len(versions1) else 0
		v2 = versions2[i] if i < len(versions2) else 0
		if v1 > v2:
			return 1
		elif v1 < v2:
			return -1
	return 0
RollName = "stacki"
