static char rcsid[] = "$Id$";
/* -----------------------------------------------------------------------
 *
 * file		$RCSfile$
 * author(s)	Mason J. Katz
 * created	10/19/00 15:33:25	mjk
 *
 * -----------------------------------------------------------------------
 *
 * 
 *
 * -----------------------------------------------------------------------
 *
 * @Copyright@
 * Copyright (c) 2000 - 2010 The Regents of the University of California
 * All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
 * https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
 * @Copyright@
 *
 * $Log$
 * Revision 1.12  2010/09/07 23:53:08  bruno
 * star power for gb
 *
 * Revision 1.11  2009/05/01 19:07:08  mjk
 * chimi con queso
 *
 * Revision 1.10  2008/10/18 00:56:01  mjk
 * copyright 5.1
 *
 * Revision 1.9  2008/03/06 23:41:44  mjk
 * copyright storm on
 *
 * Revision 1.8  2007/06/23 04:03:24  mjk
 * mars hill copyright
 *
 * Revision 1.7  2006/09/11 22:47:22  mjk
 * monkey face copyright
 *
 * Revision 1.6  2006/08/10 00:09:40  mjk
 * 4.2 copyright
 *
 * Revision 1.5  2005/10/12 18:08:41  mjk
 * final copyright for 4.1
 *
 * Revision 1.4  2005/09/16 01:02:20  mjk
 * updated copyright
 *
 * Revision 1.3  2005/05/24 21:21:57  mjk
 * update copyright, release is not any closer
 *
 * Revision 1.2  2005/03/12 00:01:52  bruno
 * minor checkin
 *
 * Revision 1.1  2005/03/01 02:02:49  mjk
 * moved from core to base
 *
 * Revision 1.12  2004/03/25 03:15:47  bruno
 * touch 'em all!
 *
 * update version numbers to 3.2.0 and update copyrights
 *
 * Revision 1.11  2003/08/15 22:34:46  mjk
 * 3.0.0 copyright
 *
 * Revision 1.10  2003/05/22 16:39:28  mjk
 * copyright
 *
 * Revision 1.9  2003/02/17 18:43:04  bruno
 * updated copyright to 2003
 *
 * Revision 1.8  2002/10/18 21:33:26  mjk
 * Rocks 2.3 Copyright
 *
 * Revision 1.7  2002/02/21 21:33:27  bruno
 * added new copyright
 *
 * Revision 1.6  2001/05/09 20:17:19  bruno
 * bumped copyright 2.1
 *
 * Revision 1.5  2001/04/10 14:16:31  bruno
 * updated copyright
 *
 * Revision 1.4  2001/02/14 20:16:34  mjk
 * Release 2.0 Copyright
 *
 * Revision 1.3  2000/11/02 05:09:34  mjk
 * Added Copyright
 *
 * Revision 1.2  2000/10/20 00:07:32  mjk
 * Cleaned usage() command
 * Fixed detach in spec file
 *
 * Revision 1.1  2000/10/19 23:12:20  mjk
 * Bumped version number
 * added detach.c
 * fixed bug in draino.c
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#ifdef __linux__
#include <libgen.h>
#endif

static void	help(FILE *fout, const char *name);
static void	usage(FILE *fout, const char *name);

static const char	*usage_name    = "Detach";
static const char	*usage_version = VERSION " ("__DATE__" "__TIME__")";
static const char	*usage_text = "[-h]";
static const char	*usage_help =
"\t-h\thelp\n"
;



int
main(int argc, char *argv[])
{
	const char	*usage_command	= (const char *)basename(argv[0]);
	int		c;
	int		child;

	opterr = 0;
	while ( (c=getopt(argc,argv,"h")) != EOF ) {
		switch ( c ) {
		case 'h':	/* help 				*/
			help(stdout, usage_command);
			exit(0);
		default:	/* usage 				*/
			usage(stderr, usage_command);
			exit(-1);
		}
	}
	argc -= optind;
	argv += optind;
	if ( argc != 1 ) {
		usage(stderr, usage_command);
		exit(-1);
	}

	switch ( (child = fork()) ) {
	case -1:
		perror("cannot fork");
		exit(-1);
	case 0:			/* child */
		execl("/bin/sh", "/bin/sh", "-c", argv[0], NULL);
		perror("execl failed");
		exit(-1);
	default:
		break;
	}

 	return 0;
} /* main */


static void
help(FILE *fout, const char *name)
{
	usage(fout, name);
	fprintf(fout, "%s", usage_help);
} /* help */
  

static void
usage(FILE *fout, const char *name)
{
	fprintf(fout,"%s - version %s\nUsage: %s %s\n",
		usage_name, usage_version, name, usage_text);
} /* usage */


