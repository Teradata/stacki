#!/opt/stack/bin/python
#
# $Id$
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.12  2010/09/07 23:53:05  bruno
# star power for gb
#
# Revision 1.11  2009/05/01 19:07:05  mjk
# chimi con queso
#
# Revision 1.10  2008/10/18 00:55:59  mjk
# copyright 5.1
#
# Revision 1.9  2008/03/06 23:41:41  mjk
# copyright storm on
#
# Revision 1.8  2007/06/23 04:03:22  mjk
# mars hill copyright
#
# Revision 1.7  2006/09/11 22:47:09  mjk
# monkey face copyright
#
# Revision 1.6  2006/08/10 00:09:31  mjk
# 4.2 copyright
#
# Revision 1.5  2006/01/25 22:22:55  bruno
# compute nodes build again
#
# Revision 1.4  2005/10/12 18:08:38  mjk
# final copyright for 4.1
#
# Revision 1.3  2005/09/16 01:02:18  mjk
# updated copyright
#
# Revision 1.2  2005/05/24 21:21:53  mjk
# update copyright, release is not any closer
#
# Revision 1.1  2005/03/01 02:02:47  mjk
# moved from core to base
#
# Revision 1.10  2004/03/25 03:15:39  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.9  2003/09/24 17:08:45  fds
# Bruno's changes for RH 9
#
# Revision 1.8  2003/08/15 22:34:46  mjk
# 3.0.0 copyright
#
# Revision 1.7  2003/05/22 16:39:27  mjk
# copyright
#
# Revision 1.6  2003/02/17 18:43:04  bruno
# updated copyright to 2003
#
# Revision 1.5  2002/10/18 21:33:26  mjk
# Rocks 2.3 Copyright
#
# Revision 1.4  2002/02/21 21:33:27  bruno
# added new copyright
#
# Revision 1.3  2001/06/14 20:56:14  mjk
# More IA64 changes
#

import sys
import pty
import os

#
# this code is a slimmed down version of the 'spawn' function in 
# 'pty.py' found in the python distribution.
#
# this file has the the termio functions removed (e.g., tcgetattr)
# because they fail when we use them with csp.
#
pid, master_fd = pty.fork()
if pid == 0:
	#
	# child process
	#
	apply(os.execle, (sys.argv[1],) + tuple(sys.argv[1:]) + (os.environ,))
else:
	#
	# parent
	#
	try:
		pty._copy(master_fd)
	except:
		pass

