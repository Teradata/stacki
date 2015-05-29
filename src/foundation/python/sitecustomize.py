import site
import os
import sys

arch = os.uname()[4]

if arch == 'x86_64':
	libdir = 'lib64'
else:
	libdir = 'lib'

path = os.path.join('/opt', 'stack', 'redhat', 'usr', libdir, 
	'python%s' % sys.version[:3], 'site-packages')

site.addsitedir(path)
