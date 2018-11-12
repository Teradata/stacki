#!/opt/stack/bin/python

import sys
import os
from stack.commands import *

sys.path.append('/tmp')
from stack_site import *

if str2bool(attributes['debug']) == True:
	os.mknod('/tmp/debug')
