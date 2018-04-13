#!/bin/bash
#
# Script to backup the mysql Cluster database, and 
# check in changes to RCS.
# 
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.13  2010/09/07 23:53:09  bruno
# star power for gb
#
# Revision 1.12  2009/05/14 23:41:12  bruno
# change the database backup to use the foundation
#
# Revision 1.11  2009/05/01 19:07:09  mjk
# chimi con queso
#
# Revision 1.10  2008/10/18 00:56:03  mjk
# copyright 5.1
#
# Revision 1.9  2008/03/06 23:41:45  mjk
# copyright storm on
#
# Revision 1.8  2007/07/15 01:39:17  phil
# explicitly set HOME so that the connection to mysql can done using
# root's .my.cnf file, which contains the apache password.
#
# Revision 1.7  2007/06/23 04:03:25  mjk
# mars hill copyright
#
# Revision 1.6  2006/09/11 22:47:28  mjk
# monkey face copyright
#
# Revision 1.5  2006/08/10 00:09:45  mjk
# 4.2 copyright
#
# Revision 1.4  2005/10/12 18:08:46  mjk
# final copyright for 4.1
#
# Revision 1.3  2005/09/16 01:02:25  mjk
# updated copyright
#
# Revision 1.2  2005/05/24 21:22:00  mjk
# update copyright, release is not any closer
#
# Revision 1.1  2005/03/01 02:03:17  mjk
# moved from core to base
#
# Revision 1.1  2004/04/13 03:21:05  fds
# Daily mysql cluster backup to RCS (phil's idea).
#
#

export HOME=/root
cd /var/db

/usr/bin/mysqldump -u apache --opt cluster > mysql-backup-cluster

# To check in multiple versions, you need to have a lock on the
# file. RCS will automatically ignore checkins for unchanged files.
ci -l -t-'stacki Cluster Database' -m`date +"%Y-%m-%d"` mysql-backup-cluster > /dev/null 2>&1
