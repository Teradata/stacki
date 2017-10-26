#!/opt/stack/bin/python3

import os
import sys
import stat

sys.path.append("/tmp")
import stack_site

f = open('/authorized_keys', 'w')
f.write("%s\n" % stack_site.authorized_key)
f.close()

os.chmod('/authorized_keys',stat.S_IRUSR)

f = open('/etc/ssh/ssh_host_ecdsa_key', 'w')
f.write("%s\n" % stack_site.host_key)
f.close()

os.chmod('/etc/ssh/ssh_host_ecdsa_key',stat.S_IRUSR)
