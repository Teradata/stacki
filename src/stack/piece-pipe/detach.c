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
 *  				Rocks(r)
 *  		         www.rocksclusters.org
 *  		         version 5.4 (Maverick)
 *  
 * Copyright (c) 2000 - 2010 The Regents of the University of California.
 * All rights reserved.	
 *  
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *  
 * 1. Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *  
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice unmodified and in its entirety, this list of conditions and the
 * following disclaimer in the documentation and/or other materials provided 
 * with the distribution.
 *  
 * 3. All advertising and press materials, printed or electronic, mentioning
 * features or use of this software must display the following acknowledgement: 
 *  
 * 	"This product includes software developed by the Rocks(r)
 * 	Cluster Group at the San Diego Supercomputer Center at the
 * 	University of California, San Diego and its contributors."
 * 
 * 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
 * neither the name or logo of this software nor the names of its
 * authors may be used to endorse or promote products derived from this
 * software without specific prior written permission.  The name of the
 * software includes the following terms, and any derivatives thereof:
 * "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
 * the associated name, interested parties should contact Technology 
 * Transfer & Intellectual Property Services, University of California, 
 * San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
 * Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
 *  
 * THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
 * BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 * BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
 * OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
 * IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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


