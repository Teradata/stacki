# $Id$
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.3  2010/09/07 23:52:53  bruno
# star power for gb
#
# Revision 1.2  2009/05/01 19:06:57  mjk
# chimi con queso
#
# Revision 1.1  2009/02/10 20:11:20  mjk
# os attr stuff for anoop
#

import stack.commands


class command(stack.commands.OSArgumentProcessor,
	stack.commands.dump.command):
	pass
	
