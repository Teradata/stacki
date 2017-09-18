# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import configparser
import stack.api


def GetHostname(host='localhost'):
	"""
	Takes the name, ip, or mac of any network interface of the
	HOST and returns the canonical name of the host.  The canonical
	name if the value store in the NODES table of the cluster database.

	If the HOST could not be found it returns None.
	"""

	result = stack.api.Call('list host', [ host ])

	if result:
		assert len(result) == 1
		return result[0]['host']
	
	return None


def GetAttr(attribute):
	"""
	Returns the value of the specified ATTRIBUTE for the caller's host.
	If no attribute is define it returns None.
	"""
	return GetHostAttr('localhost', attribute)


def GetHostAttr(host, attribute):
	"""
	Returns the value of the specified ATTRIBUTE for the given
	HOST.  If no attribute is define it returns None.

	If a profile.cfg file is found read the attribute from there
	rather than from the database.
	"""

	value = None

	cfg = configparser.RawConfigParser()
	cfg.read(os.path.join(os.sep, 'opt', 'stack', 'etc', 'profile.cfg'))
	try:
		value = cfg.get('attr', attribute)
	except:
		result = stack.api.Call('list host attr', 
					[host, 'attr=%s' % attribute])
		if result:
			assert len(result) == 1
			value = result[0]['value']
		
	return value


if __name__ == "__main__":
	print('GetHostname() ->', GetHostname())
	print('GetHostAttr("localhost", "os") ->', GetHostAttr('localhost', 'os'))
