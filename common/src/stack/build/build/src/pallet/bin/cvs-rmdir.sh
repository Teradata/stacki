#!/bin/bash
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
# Revision 1.5  2009/05/01 19:07:10  mjk
# chimi con queso
#
# Revision 1.4  2008/10/18 00:56:03  mjk
# copyright 5.1
#
# Revision 1.3  2008/03/06 23:41:46  mjk
# copyright storm on
#
# Revision 1.2  2008/02/01 19:09:09  mjk
# safer
#
# Revision 1.1  2008/02/01 18:58:12  mjk
# Use this to remove dead rolls from CVS
#

function rmfiles {
	pushd $@
	for file in *; do
		if [ -f $file ]; then
			/bin/rm -f $file
			cvs rm $file
		fi
		if [ -d $file ] && [ $file != "CVS" ]; then
			
			rmfiles $file
		fi
	done
	popd
}

if [ "$1" == "" ]; then
	echo "usage: $0 dir"
	exit -1
fi

rmfiles $1
