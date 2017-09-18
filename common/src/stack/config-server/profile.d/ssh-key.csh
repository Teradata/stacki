#
# $Id$
#
# generate a ssh key if one doesn't exist
#
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
#
# $Log$
# Revision 1.5  2010/09/07 23:53:03  bruno
# star power for gb
#
# Revision 1.4  2009/05/01 19:07:05  mjk
# chimi con queso
#
# Revision 1.3  2008/10/18 00:55:58  mjk
# copyright 5.1
#
# Revision 1.2  2008/03/06 23:41:41  mjk
# copyright storm on
#
# Revision 1.1  2007/08/13 19:31:00  bruno
# get the spec file out of rocks-config. this requires building a new
# package named : rocks-config-server
#
# Revision 1.7  2007/06/23 04:03:21  mjk
# mars hill copyright
#
# Revision 1.6  2006/09/11 22:47:05  mjk
# monkey face copyright
#
# Revision 1.5  2006/08/10 00:09:28  mjk
# 4.2 copyright
#
# Revision 1.4  2005/10/12 18:08:34  mjk
# final copyright for 4.1
#
# Revision 1.3  2005/09/16 01:02:14  mjk
# updated copyright
#
# Revision 1.2  2005/05/24 21:21:50  mjk
# update copyright, release is not any closer
#
# Revision 1.1  2005/03/01 02:02:43  mjk
# moved from core to base
#
# Revision 1.12  2004/03/25 03:15:29  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.11  2003/08/15 22:34:46  mjk
# 3.0.0 copyright
#
# Revision 1.10  2003/05/22 16:39:27  mjk
# copyright
#
# Revision 1.9  2003/02/17 18:43:04  bruno
# updated copyright to 2003
#
# Revision 1.8  2002/10/18 21:33:26  mjk
# Rocks 2.3 Copyright
#
# Revision 1.7  2002/02/21 21:33:27  bruno
# added new copyright
#
# Revision 1.6  2001/05/09 20:17:13  bruno
# bumped copyright 2.1
#
# Revision 1.5  2001/04/10 14:16:27  bruno
# updated copyright
#
# Revision 1.4  2001/02/14 20:16:29  mjk
# Release 2.0 Copyright
#
# Revision 1.3  2001/02/02 18:34:08  bruno
# add auto freshing of kickstart files after root builds it's ssh-key
#
# Revision 1.2  2000/12/12 23:45:39  bruno
# tweaks to fix dumbass mistakes
#
# Revision 1.1  2000/12/12 23:36:49  bruno
# initial release
#

/bin/bash /etc/profile.d/ssh-key.sh
