# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#

import os
import stack.commands


class Plugin(stack.commands.Plugin):

	def provides(self):
		return 'ca'


	def run(self, args):
		(oldhost, oldip, password) = args

		shortname = self.owner.getHostAttr('localhost',
			'Kickstart_PrivateHostname')
		domainname = self.owner.getHostAttr('localhost',
			'Kickstart_PublicDNSDomain')

		print('Updating CA certificates')

		newfile = []

		file = open('/etc/security/ca/ca.cfg', 'r')
		for line in file.readlines():
			if line[0:len('commonName_default')] == \
					'commonName_default':
				newfile.append('commonName_default = %s.%s' %
					(shortname, domainname))
			else:
				newfile.append(line[:-1])
		file.close()

		file = open('/tmp/ca.cfg', 'w+')
		file.write('\n'.join(newfile))
		file.write('\n')
		file.close()

		os.system('/bin/mv /tmp/ca.cfg /etc/security/ca/ca.cfg')
		os.system('/bin/chmod 500 /etc/security/ca/ca.cfg')

		#
		# make a new cert
		#
		cmd = 'cd /etc/security/ca; '
		cmd += '/usr/bin/openssl req -new -x509 -extensions v3_ca '
		cmd += '-nodes -keyout ca.key -days 5000 -batch '
		cmd += '-config ca.cfg > ca.crt 2> /dev/null; '
		cmd += 'chmod 0400 ca.key; '
		cmd += 'chmod 0444 ca.crt; '
		os.system(cmd)

		#
		# update the httpd certs
		#
		os.system('cp /etc/security/ca/ca.crt /etc/httpd/conf/ssl.ca/')
		os.system('make -C /etc/httpd/conf/ssl.ca > /dev/null 2>&1')

		#
		# Make a Certificate for Mod_SSL
		#
		cmd = 'cd /etc/pki/tls ; '
		cmd += '/usr/bin/openssl req -new -nodes -config '
		cmd += '/etc/security/ca/ca.cfg -keyout private/localhost.key '
		cmd += ' -subj "'
		cmd += '/C=%s/ ' % self.owner.getHostAttr('localhost',
			'Info_CertificateCountry')
		cmd += 'ST=%s/ ' % self.owner.getHostAttr('localhost',
			'Info_CertificateState')
		cmd += 'L=%s/ ' % self.owner.getHostAttr('localhost',
			'Info_CertificateLocality')
		cmd += 'O=%s/ ' % self.owner.getHostAttr('localhost',
			'Info_CertificateOrganization')
		cmd += 'OU=%s/ ' % self.owner.getHostAttr('localhost',
			'Kickstart_PrivateHostname')
		cmd += 'CN=%s.%s" ' % (shortname, domainname)
		cmd += '> certs/localhost.csr 2> /dev/null ; '
		cmd += 'chmod 0400 private/localhost.key'
		os.system(cmd)

		#
		# Sign the Request with our CA
		#
		cmd = 'cd /etc/security/ca; '
		cmd += '/usr/bin/openssl x509 -req -days 2000 -CA ca.crt '
		cmd += '-CAkey ca.key -CAserial ca.serial '
		cmd += '< /etc/pki/tls/certs/localhost.csr '
		cmd += '> /etc/pki/tls/certs/localhost.crt 2> /dev/null ; '
		cmd += 'chmod 0444 /etc/pki/tls/certs/localhost.crt '
		os.system(cmd)

