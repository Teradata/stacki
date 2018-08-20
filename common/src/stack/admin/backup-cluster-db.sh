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

export HOME=/root
cd /var/db

/usr/bin/mysqldump --defaults-file=/etc/apache.my.cnf --all-databases  > mysql-backup-cluster
/usr/bin/mysqldump --defaults-file=/opt/stack/etc/django.my.cnf django > mysql-backup-django

# To check in multiple versions, you need to have a lock on the
# file. RCS will automatically ignore checkins for unchanged files.
ci -l -t-'stacki Cluster Database' -m`date +"%Y-%m-%d"` mysql-backup-cluster > /dev/null 2>&1
ci -l -t-'stacki Django Database' -m`date +"%Y-%m-%d"` mysql-backup-django > /dev/null 2>&1
