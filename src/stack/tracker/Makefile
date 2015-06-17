# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
#  
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
#  
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@


PKGROOT         = /opt/stack
ROLLROOT	= ../../..
DEPENDS.FILES	= $(wildcard *.c) $(wildcard *.h)

include $(STACKBUILD)/etc/CCRules.mk

INCLUDE	= -I/usr/include/apr-1 -I/opt/stack/fcgi/include -I/opt/stack/include
#LIBS	= -L/opt/stack/lib -lcurl
#LIBS	= -lcurl -lssl -lidn -lgssapi_krb5 -lkrb5 -lk5crypto -lkrb5support -lpthread -lcrypto -lz -ldl -lcom_err -lkeyutils -lresolv -lselinux -lsepol
#LIBS	= -L /opt/stack/curl/lib/ -lcurl
LIBS	= -lcurl -lcrypto
CFLAGS	= -Wall -g `apr-1-config --cppflags --cflags`
#CFLAGS	+= -DTIMEIT 
#CFLAGS	+= -DDEBUG
EXECS	= tracker-client unregister-file tracker-server peer-done stop-server

MYSQL	= 1

ifeq ($(MYSQL),1)
SERVERLIBS	= -L/opt/stack/lib/mysql -lmysqlclient
CFLAGS		+= -DWITH_MYSQL 
endif

build:	$(EXECS)

tracker-client:	tracker-client.c client.c lib.c checkmd5.c
	$(CC) $(INCLUDE) $(CFLAGS) -DFASTCGI -o tracker-client tracker-client.c \
		client.c lib.c checkmd5.c $(LIBS) /opt/stack/fcgi/lib/libfcgi.a

unregister-file:	unregister-file.c client.c lib.c
	$(CC) $(INCLUDE) $(CFLAGS) -o unregister-file unregister-file.c \
		client.c lib.c $(LIBS)

tracker-server:		server.o lib.o shuffle.o
	$(CC) $(INCLUDE) $(CFLAGS) -pg -o tracker-server server.o lib.o shuffle.o \
		$(LIBS) $(SERVERLIBS)

lib.o:	lib.c
	$(CC) $(INCLUDE) $(CFLAGS) -c lib.c

shuffle.o:	shuffle.c
	$(CC) $(INCLUDE) $(CFLAGS) -c shuffle.c

server.o:	server.c
	$(CC) $(INCLUDE) $(CFLAGS) -c server.c

hashit:		hashit.c
	$(CC) $(INCLUDE) $(CFLAGS) -o hashit hashit.c lib.c $(LIBS)

peer-done:	peer-done.c
	$(CC) $(INCLUDE) $(CFLAGS) -o peer-done peer-done.c client.c lib.c \
		$(LIBS)

stop-server:	stop-server.c
	$(CC) $(INCLUDE) $(CFLAGS) -o stop-server stop-server.c client.c lib.c \
		$(LIBS)

install::
	mkdir -p $(ROOT)/$(PKGROOT)/bin
	cp $(EXECS) $(ROOT)/$(PKGROOT)/bin

clean::
	rm -f $(EXECS)
	rm -f *.o

