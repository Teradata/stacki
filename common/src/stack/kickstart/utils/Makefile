# --------------------------------------------------- -*- Makefile -*- --
# $Id$
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.11  2010/09/07 23:53:07  bruno
# star power for gb
#
# Revision 1.10  2009/05/01 19:07:07  mjk
# chimi con queso
#
# Revision 1.9  2008/10/18 00:56:01  mjk
# copyright 5.1
#
# Revision 1.8  2008/03/06 23:41:44  mjk
# copyright storm on
#
# Revision 1.7  2007/06/23 04:03:23  mjk
# mars hill copyright
#
# Revision 1.6  2006/09/11 22:47:17  mjk
# monkey face copyright
#
# Revision 1.5  2006/08/10 00:09:38  mjk
# 4.2 copyright
#
# Revision 1.4  2005/10/12 18:08:40  mjk
# final copyright for 4.1
#
# Revision 1.3  2005/09/16 01:02:19  mjk
# updated copyright
#
# Revision 1.2  2005/05/24 21:21:55  mjk
# update copyright, release is not any closer
#
# Revision 1.1  2005/03/01 02:02:49  mjk
# moved from core to base
#
# Revision 1.3  2004/03/25 03:15:41  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.2  2003/08/15 22:34:46  mjk
# 3.0.0 copyright
#
# Revision 1.1  2003/08/13 23:39:49  fds
# Some kickstart utilities.
# Makes the RPMs arch-dependant, unfortunately.
#
#

RELEASE = 1
SRCS = $(wildcard *.c)
HEADERS = $(wildcard *.h)

BIN=$(SRCS:.c=)

all: $(BIN)

%: %.c $(HEADERS)
	gcc  -o $@ $<

clean::
	rm -f *.o $(BIN)


