#!/opt/stack/bin/python3

#
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import os
import sys
import json

import wsclient

#
# EXAMPLE CLIENT APPLICATION TO ACCESS WEBSERVICE
#

def getCredentialsFile(args):
	if '-f' in args:
		idx = args.index('-f')
		cred_file = args.pop(idx+1)
		args.pop(idx)
	else:
		homedir = os.getenv("HOME")
		cred_file = "%s/stacki-ws.cred" % homedir
	if not os.path.exists(cred_file):
		sys.stderr.write('Cannot file credential file %s\n' % cred_file)
		sys.exit(1)
	return cred_file

def parseCredentials(cred_file):
	cred = open(cred_file, 'r')
	j = json.load(cred)
	hostname = j['hostname']
	username = j['username']
	key	 = j['key']
	return (hostname, username, key)

if __name__ == '__main__':
	cred_file = getCredentialsFile(sys.argv)
	hostname, username, key = parseCredentials(cred_file)

	wsClient = wsclient.StackWSClient(hostname, username, key)
	wsClient.login()

	if len(sys.argv) < 2:
		sys.exit(1)

	cmd = ' '.join(sys.argv[1:])
	out = wsClient.run(cmd)
	print(out)
