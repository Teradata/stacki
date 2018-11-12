#!/opt/stack/bin/python

import subprocess
import os

debug = open('/tmp/stacki-profile.debug', 'w')

for i in os.environ:
	debug.write('%s %s\n' % (i, os.environ[i]))	

debug.close()

#
# make sure the target directory is there
#
try:
	os.makedirs('/tmp/profile')
except:
	pass

#
# get the interfaces
#
linkcmd = [ 'ip', '-oneline', 'link', 'show' ]

p = subprocess.Popen(linkcmd, stdout = subprocess.PIPE)

interface_number = 0

curlcmd = [ '/usr/bin/curl', '--local-port', '1-100',
	'-o', '/tmp/stacki-profile.xml' ]

o, e = p.communicate()
for line in o.split('\n'):
        interface = None
        hwaddr = None

        tokens = line.split()
        if len(tokens) > 11:
                # print 'tokens: %s' % tokens
                #
                # strip off last ':'
                #
                interface = tokens[1].strip()[0:-1]

                for i in range(2, len(tokens)):
                        if tokens[i] == 'link/ether':
                                #
                                # we know the next token is the ethernet MAC
                                #
                                hwaddr = tokens[i+1]
                                break

                if interface and hwaddr:
			curlcmd.append('--header')
			curlcmd.append('X-RHN-Provisioning-MAC-%d: %s %s'
				% (interface_number, interface, hwaddr))

                        interface_number += 1

curlcmd.append('-k')

#
# get the number of CPUs
#
numcpus = 0
file = open('/proc/cpuinfo', 'r')
for line in file.readlines():
	l = line.split(':')
	if l[0].strip() == 'processor':
		numcpus += 1
file.close()

request = os.environ['url']
request += "&profile=full"
curlcmd.append(request)

out = open("/tmp/stdout.txt","w") 
err = open("/tmp/stderr.txt","w")

subprocess.call(curlcmd, stdout=out, stderr=err)
out.close()
err.close()
