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
# Revision 1.8  2007/06/23 04:03:21  mjk
# mars hill copyright
#
# Revision 1.7  2006/09/11 22:47:05  mjk
# monkey face copyright
#
# Revision 1.6  2006/08/10 00:09:28  mjk
# 4.2 copyright
#
# Revision 1.5  2005/10/19 12:59:49  bruno
# remove dead code that causes an error message on first login as root
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
# Revision 1.28  2005/01/06 16:12:39  bruno
# make sure /root/.ssh is readable by apache.
#
# fix for bug 102.
#
# Revision 1.27  2004/08/25 05:25:38  bruno
# move from ssh v1 to ssh v2
#
# (bug 17)
#
# Revision 1.26  2004/03/25 03:15:29  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.25  2003/08/15 22:34:46  mjk
# 3.0.0 copyright
#
# Revision 1.24  2003/05/22 16:39:27  mjk
# copyright
#
# Revision 1.23  2003/05/21 18:57:31  mjk
# grid integration checkpoint
#
# Revision 1.22  2003/02/17 18:43:04  bruno
# updated copyright to 2003
#
# Revision 1.21  2003/02/12 01:19:17  fds
# Dont need quotes around var.
#
# Revision 1.20  2003/02/12 01:18:21  fds
# INTERACTIVE can only be false or implied true. Need dodouble [[s around test.
#
# Revision 1.19  2003/02/11 17:52:12  bruno
# one more pass on the interactive stuff
#
# Revision 1.18  2003/02/11 17:10:24  bruno
# changed around the interactive stuff a bit.
#
# Revision 1.17  2003/02/10 23:42:16  fds
# A safer way to invoke ssh-host checking.
#
# Revision 1.16  2003/02/07 01:12:25  fds
# An additional check.
#
# Revision 1.15  2002/10/18 21:33:26  mjk
# Rocks 2.3 Copyright
#
# Revision 1.14  2002/08/27 23:30:17  bruno
# removed SSL cert creation
#
# Revision 1.13  2002/05/07 22:53:50  bruno
# added '-t' flag for new version of ssh-keygen
#
# Revision 1.12  2002/02/21 21:33:27  bruno
# added new copyright
#
# Revision 1.11  2001/05/09 20:17:13  bruno
# bumped copyright 2.1
#
# Revision 1.10  2001/04/10 14:16:27  bruno
# updated copyright
#
# Revision 1.9  2001/03/06 15:11:45  bruno
# if root user, then make sure ssh and cert permissions are right for
# cluster-dist
#
# Revision 1.8  2001/02/20 15:53:37  bruno
# rebuild kickstart files only once.
#
# Revision 1.7  2001/02/14 21:42:33  mjk
# Rebuild kickstart files after ss-genca
#
# Revision 1.6  2001/02/14 20:16:30  mjk
# Release 2.0 Copyright
#
# Revision 1.5  2001/02/14 19:43:28  mjk
# Also generate the SSL CA Certificate
#
# Revision 1.4  2001/02/06 21:10:22  bruno
# fixed the 'find' so it will automount /home/install/
#
# Revision 1.3  2001/02/02 18:34:09  bruno
# add auto freshing of kickstart files after root builds it's ssh-key
#
# Revision 1.2  2000/12/12 23:45:39  bruno
# tweaks to fix dumbass mistakes
#
# Revision 1.1  2000/12/12 23:36:49  bruno
# initial release
#

# If we are interactive and don't have a public key, send prompt.
if [[ $INTERACTIVE != "false" ]] && [ ! -f $HOME/.ssh/id_rsa.pub ]
then
	ssh-keygen -t rsa -N "" -f $HOME/.ssh/id_rsa > /dev/null 2>&1

	cat $HOME/.ssh/id_rsa.pub >> $HOME/.ssh/authorized_keys

	chmod 600 $HOME/.ssh/authorized_keys
	chmod g-w $HOME
fi

