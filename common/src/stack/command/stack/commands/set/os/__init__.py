# $Id$
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.4  2010/09/07 23:53:02  bruno
# star power for gb
#
# Revision 1.3  2009/05/01 19:07:04  mjk
# chimi con queso
#
# Revision 1.2  2009/02/10 20:11:20  mjk
# os attr stuff for anoop
#
# Revision 1.1  2009/01/24 02:04:29  mjk
# - more ROCKDEBUG stuff (now to stderr)
# - os attr commands (still incomplete)
# - fix ssl code
#

import stack.commands
from stack.commands import OSArgProcessor

class command(OSArgProcessor, stack.commands.set.command):
	pass
