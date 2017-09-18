#!/bin/bash
#
# 
# Copy specified rolls to mirror. If no rolls are specified, 
# copy all rolls in current dir to mirror.
# For use during roll development and on central servers.
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
# 
# $Log$
# Revision 1.2  2010/09/07 23:53:05  bruno
# star power for gb
#
# Revision 1.1  2010/06/22 21:07:44  mjk
# build env moving into base roll
#
# Revision 1.11  2009/05/01 19:07:10  mjk
# chimi con queso
#
# Revision 1.10  2008/10/18 00:56:03  mjk
# copyright 5.1
#
# Revision 1.9  2008/03/06 23:41:46  mjk
# copyright storm on
#
# Revision 1.8  2007/06/23 04:03:26  mjk
# mars hill copyright
#
# Revision 1.7  2006/09/11 22:47:30  mjk
# monkey face copyright
#
# Revision 1.6  2006/08/10 00:09:47  mjk
# 4.2 copyright
#
# Revision 1.5  2006/01/10 18:02:52  mjk
# *** empty log message ***
#
#

umount /mnt/cdrom 2> /dev/null

if [ $# -ne 0 ]
then
	r=$*
else
	r=`ls *iso`
fi

for i in $r
do
	mount -o loop $i /mnt/cdrom
	rocks-dist --clean copyroll
	umount /mnt/cdrom
	echo "Copied $i"
done
