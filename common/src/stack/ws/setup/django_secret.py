#!/opt/stack/bin/python3
#
# @copyright@
# @copyright@
#


import string
import random

# Remove all whitespaces
s = string.printable.strip()

# Create secret key
secret = ''.join(random.choice(s) for _ in range(50))

# Write secret key to file
f = open('/opt/stack/etc/django.secret','w')
f.write("%s\n" % secret)
f.close()
