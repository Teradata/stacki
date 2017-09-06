static char rcsid[] = "$Id$";
/* -----------------------------------------------------------------------
 *
 * Allow a non-root user (depending on the permissions for this executable)
 * to read the 411 shared key. This app is intended to run setuid root.
 *
 * @Copyright@
 * Copyright (c) 2000 - 2010 The Regents of the University of California
 * All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
 * https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
 * @Copyright@
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
 * Revision 1.1  2005/02/12 02:27:54  fds
 * 411 second generation: safer, thanks to master-only RSA keypair; all files
 * are now signed for integrity. Faster for master, since we run the random
 * number generator less (only once per cluster lifetime rather than once per
 * encryption).  Keys are kept in /etc/411-security. Amen.
 *
 * Revision 1.6  2004/03/25 03:15:41  bruno
 * touch 'em all!
 *
 * update version numbers to 3.2.0 and update copyrights
 *
 * Revision 1.5  2003/09/27 00:19:00  fds
 * Prevent a segfault during error handling.
 *
 * Revision 1.4  2003/09/15 22:57:59  fds
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
#include <errno.h>

/* Hardcoded file to read for security. */
#define FILENAME "/etc/411-security/shared.key"

#define MYUSER "apache"

int
main(int argc, char *argv[])
{
	FILE *f;
	/* Lines in our file are cut to 80 chars. */
	char line[128];
	int me = getuid();
	struct passwd *caller;

	caller = getpwuid(me);
	/* Allow root to read file as well. */
	if (me && strcmp(caller->pw_name, MYUSER))
	{
		fprintf(stderr, 
		  "read-private-key: Not run by user '%s' (or root), exiting.\n", 
		  MYUSER);
		return -1;
	}

	f=fopen(FILENAME, "r");
	if (!f)
	{
		fprintf(stderr, "Could not open '%s' for reading.\n",
			FILENAME);
		return -1;
	}

	while ( fgets(line, sizeof(line), f) )
	{
		printf("%s", line);
	}
	
	fclose(f);
	
	return 0;
}
