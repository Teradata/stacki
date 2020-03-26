# $Id$
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.2  2010/09/07 23:53:03  bruno
# star power for gb
#
# Revision 1.1  2010/06/07 23:50:12  bruno
# added a command to swap two interfaces
#
#

import stack.commands
from stack.commands import HostArgProcessor

class command(HostArgProcessor, stack.commands.swap.command):
	pass

