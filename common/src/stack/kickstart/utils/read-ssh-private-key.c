static char rcsid[] = "$Id$";
/* -----------------------------------------------------------------------
 *
 * Allow a non-root user (depending on the permissions for this executable)
 * to read the Cluster Private Key. This app is intended to run setuid root.
 *
 * @rocks@
 * Copyright (c) 2000 - 2010 The Regents of the University of California
 * All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
 * https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
 * @rocks@
 *
 * test with: gcc -o read-private-key read-private-key.c
 * $Log$
 * Revision 1.11  2010/09/07 23:53:07  bruno
 * star power for gb
 *
 * Revision 1.10  2009/05/01 19:07:07  mjk
 * chimi con queso
 *
 * Revision 1.9  2008/10/18 00:56:01  mjk
 * copyright 5.1
 *
 * Revision 1.8  2008/03/06 23:41:44  mjk
 * copyright storm on
 *
 * Revision 1.7  2007/06/23 04:03:23  mjk
 * mars hill copyright
 *
 * Revision 1.6  2006/09/11 22:47:17  mjk
 * monkey face copyright
 *
 * Revision 1.5  2006/08/10 00:09:38  mjk
 * 4.2 copyright
 *
 * Revision 1.4  2005/10/12 18:08:40  mjk
 * final copyright for 4.1
 *
 * Revision 1.3  2005/09/16 01:02:19  mjk
 * updated copyright
 *
 * Revision 1.2  2005/05/24 21:21:55  mjk
 * update copyright, release is not any closer
 *
 * Revision 1.1  2005/03/01 02:02:49  mjk
 * moved from core to base
 *
 * Revision 1.6  2004/03/25 03:15:41  bruno
 * touch 'em all!
 *
 * update version numbers to 3.2.0 and update copyrights
 *
 * Revision 1.5  2003/09/27 00:19:00  fds
 * Prevent a segfault during error handling.
 *
 * Revision 1.4  2003/09/17 22:13:20  fds
 * Report correct filename on read error
 *
 * Revision 1.3  2003/09/17 21:09:24  fds
 * Correctly reads binary data
 *
 * Revision 1.2  2003/09/15 23:03:36  fds
 * Small change.
 *
 * Revision 1.1  2003/09/15 22:57:59  fds
 * SetUID app for reading SSH keys.
 *
 * Revision 1.3  2003/08/15 22:34:46  mjk
 * 3.0.0 copyright
 *
 * Revision 1.2  2003/08/13 23:46:38  fds
 * Allow root to run as well. Good for debugging.
 *
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pwd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>

/* Hardcoded file to read for security. */
#define FILENAME "/etc/ssh"

#define MYUSER "apache"

/* The different kinds of keys. */
#define RSA1	1
#define RSA	2
#define DSA	3
#define ECDSA	4
#define ED25519	5

int
main(int argc, char *argv[])
{
	int f, n;
	/* Lines in our file are cut to 80 chars. */
	char line[128];
	char *keyfile;
	int me = getuid();
	int mode = 0;
	struct passwd *caller;

	caller = getpwuid(me);
	/* Allow root to read file as well. */
	if (me && strcmp(caller->pw_name, MYUSER))
	{
		fprintf(stderr, 
			"read-ssh-private-key: Not run by user '%s' (or root), exiting.\n", 
			MYUSER);
		return -1;
	}
	
	if (argc > 1)
	{
	  if (!strncmp("RSA1", argv[1], 4))
		mode = RSA1;
	  else if (!strncmp("RSA", argv[1], 3))
		mode = RSA;
	  else if (!strncmp("DSA", argv[1], 3))
		mode = DSA;
	  else if (!strncmp("ECDSA", argv[1], 5))
		mode = ECDSA;
	  else if (!strncmp("ED25519", argv[1], 5))
		mode = ED25519;
	}
	
	switch (mode)
	{
	  case RSA1:
		keyfile = FILENAME "/ssh_host_key";
		break;
	  case RSA:
		keyfile = FILENAME "/ssh_host_rsa_key";
		break;
	  case DSA:
		keyfile = FILENAME "/ssh_host_dsa_key";
		break;
	  case ECDSA:
		keyfile = FILENAME "/ssh_host_ecdsa_key";
		break;
	  case ED25519:
		keyfile = FILENAME "/ssh_host_ed25519_key";
		break;
	  default:
		fprintf(stderr, "Please specify a key: RSA1 | RSA | DSA | ECDSA | ED25519\n");
		return 1;
	}

	f=open(keyfile, O_RDONLY);
	if (f<0)
	{
		fprintf(stderr, "Could not open '%s' for reading.\n",
			keyfile);
		return -1;
	}

		
	while ( (n = read(f, line, sizeof(line))) > 0)
	{
		write(1, line, n);
	}
	
	close(f);
	
	return 0;
}
