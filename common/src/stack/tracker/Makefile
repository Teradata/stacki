# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@
#
# @Copyright@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
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
SERVERLIBS	= -L/opt/stack/$(LIB) -lmysqlclient
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

