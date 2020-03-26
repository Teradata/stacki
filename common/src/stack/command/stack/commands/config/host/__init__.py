# $Id$
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.5  2010/09/07 23:52:51  bruno
# star power for gb
#
# Revision 1.4  2009/05/01 19:06:56  mjk
# chimi con queso
#
# Revision 1.3  2008/10/18 00:55:48  mjk
# copyright 5.1
#
# Revision 1.2  2008/03/06 23:41:36  mjk
# copyright storm on
#
# Revision 1.1  2007/12/10 21:28:34  bruno
# the base roll now contains several elements from the HPC roll, thus
# making the HPC roll optional.
#
# this also includes changes to help build and configure VMs for V.
#
#

import stack.commands
from stack.commands import HostArgProcessor

class command(HostArgProcessor, stack.commands.config.command):
	pass

