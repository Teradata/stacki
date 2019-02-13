#!/opt/stack/bin/python3
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import os
import cgi
import syslog
import json
import stack.api

syslog.openlog('setPxeBoot.cgi', syslog.LOG_PID, syslog.LOG_LOCAL0)

#
# get the name of the node that is issuing the request
#
ipaddr = None
if 'REMOTE_ADDR' in os.environ:
	ipaddr = os.environ['REMOTE_ADDR']
if not ipaddr:
	sys.exit(-1)
	
syslog.syslog(syslog.LOG_INFO, 'remote addr %s' % ipaddr)

# 'params' field should be a python dictionary of the form:
#
# { 'action': value }
#
# It is json encoded for transport to keep things simple, and
# help us only treat the values as data.

form = cgi.FieldStorage()
params = None
action = None
try:
	params = form['params'].value
	try:
		params = json.loads(params)
		try:
			action = params['action']
		except:
			syslog.syslog(syslog.LOG_ERR, 'no action speficied')
	except:
		syslog.syslog(syslog.LOG_ERR, 'invalid params %s' % params)
except:
	syslog.syslog(syslog.LOG_ERR, 'missing params')

	
# The above let's us set the boot action to anything (e.g. 'install') but
# here we lock thing down to only allow a reset to 'os'.

if action == 'os':
	stack.api.Call('set host boot', [ ipaddr, 'action=%s' % action ])
	stack.api.Call('set host attr', [ ipaddr, 'attr=nukedisks',
		'value=false'])
	stack.api.Call('set host attr', [ ipaddr, 'attr=nukecontroller',
		'value=false'])
	stack.api.Call('set host attr', [ ipaddr, 'attr=secureerase',
		'value=false'])
	
print('Content-type: application/octet-stream')
print('Content-length: %d' % (len('')))
print('')
print('')

syslog.closelog()
