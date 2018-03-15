# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import sys
import subprocess
import json

__stack__ = '/opt/stack/bin/stack'

rc = None


def ReturnCode():
	"""
	Get the return code of the previously run command.
	"""
	return rc


def Call(cmd, args=None, format='json', sudo=False, *, stderr=True):
	"""
	Call the Stack Command Line and return a python dictionary as the
	result.  Currently only works with list commands.

	Example:
		result = stack.api.Call('list network', [ 'private' ])
	"""

	global rc

	if not os.path.exists(__stack__):
		# Bailout if stack command is missing (backend nodes)
		return [ ]
	
	command = cmd.replace('.', ' ').strip().split()
	
	if sudo:
		list = [ sudo ]
	else:
		list = [ ]
	list.append(__stack__)
	list.extend(command)
	if args:
		list.extend(args)

	if command[0] == 'list':
		list.append('output-format=%s' % format)
	
	s = None
	p = subprocess.Popen(list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
	for line in p.stdout.readlines():
		if not s:
			s = line
		else:
			s += line
	if stderr: # allow caller to see or ignore stdout
		for line in p.stderr.readlines():
			sys.stderr.write(line)
		
	rc = p.wait()
	if rc:
		return [ ]

	if command[0] == 'list':
		if s:
			return json.loads(s)
		return [ ]
	
	if s:
		return s.split('\n')
	return [ ]


