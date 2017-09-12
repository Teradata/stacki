# $Id$
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @Copyright@
#
# $Log$
# Revision 1.2  2010/09/07 23:52:53  bruno
# star power for gb
#
# Revision 1.1  2009/06/10 17:40:26  mjk
# - new verb interate
# - every object should have an iterate (right now just host)
# - '%' wildcard stuff should go into pylib
#

import stack.commands


class command(stack.commands.Command):
	MustBeRoot = 0
