static char rcsid[] = "$Id$";
/* -----------------------------------------------------------------------
 *
 * file		$RCSfile$
 * author(s)	Mason J. Katz
 * created	10/13/00 14:34:19	mjk
 *
 * -----------------------------------------------------------------------
 *
 * Creates a control system with pipes.  See buildgraph comment for
 * details.
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
 * Revision 1.15  2004/03/25 03:15:47  bruno
 * touch 'em all!
 *
 * update version numbers to 3.2.0 and update copyrights
 *
 * Revision 1.14  2003/08/15 22:34:46  mjk
 * 3.0.0 copyright
 *
 * Revision 1.13  2003/05/22 16:39:28  mjk
 * copyright
 *
 * Revision 1.12  2003/02/17 18:43:04  bruno
 * updated copyright to 2003
 *
 * Revision 1.11  2002/10/18 21:33:26  mjk
 * Rocks 2.3 Copyright
 *
 * Revision 1.10  2002/02/21 21:33:27  bruno
 * added new copyright
 *
 * Revision 1.9  2001/05/09 20:17:19  bruno
 * bumped copyright 2.1
 *
 * Revision 1.8  2001/04/10 14:16:31  bruno
 * updated copyright
 *
 * Revision 1.7  2001/02/14 20:16:34  mjk
 * Release 2.0 Copyright
 *
 * Revision 1.6  2000/11/02 05:09:34  mjk
 * Added Copyright
 *
 * Revision 1.5  2000/10/20 00:07:32  mjk
 * Cleaned usage() command
 * Fixed detach in spec file
 *
 * Revision 1.4  2000/10/19 19:22:28  mjk
 * Cleanup on CSP
 * Added draino.c
 *
 * Revision 1.3  2000/10/17 22:12:19  bruno
 * updated help
 *
 * Revision 1.2  2000/10/17 05:36:04  bruno
 * spelling error
 *
 * Revision 1.1  2000/10/17 00:36:48  mjk
 * Initial Checkin
 *
 */

#include <stdio.h>
#include <signal.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#ifdef __linux__
#include <libgen.h>
#endif

#define PIPE_READ	0
#define PIPE_WRITE	1
#define BUFLEN		1024

#ifndef max
#define max(a,b)	(a) > (b) ? (a) : (b)
#endif


static void	help(FILE *fout, const char *name);
static void	usage(FILE *fout, const char *name);
static int	buildgraph(const char *cmd);
static void	duplicate(int fd1, int fd2);
static void	multiplex(int fd1, int fd2);
static int	attach(int in, int out);

static const char	*usage_name    = "Control System Pipe";
static const char	*usage_version = VERSION " ("__DATE__"  "__TIME__")";
static const char	*usage_text = "[-h] \"command\"";
static const char	*usage_help =
"\t-h\thelp\n"
;



int
main(int argc, char *argv[])
{
	const char	*usage_command = (const char *)basename(argv[0]);
	int		c;

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

 	return buildgraph(argv[0]);
} /* main */


/*
 * Create the Control System
 *
 * -------->  0  ----0---->  1  ----1---->  2  -------->
 *            ^                             |
 *            |                             |
 *            +--------------2--------------+
 *
 * node[0]: combines stdin and edge[2]
 * node[1]: command
 * node[2]: duplicates edge[1] onto stdout and edge[2]
 *
 * If any node dies the others are killed.  Return value is
 * the return code of the normally terminated process.
 */
int
buildgraph(const char *cmd)
{
	int	edge[3][2];
	pid_t	node[3];
	pid_t	child;
	int	retval;
	int	i;
	

	if ( pipe(edge[0]) || pipe(edge[1]) || pipe(edge[2]) ) {
		perror("cannot create pipes");
		exit(-1);
	}

				/* Multiplexer */
	switch ( (node[0] = fork()) ) {
	case -1:
		perror("cannot fork");
		exit(-1);
	case 0:			/* child */
		if ( !attach(STDIN_FILENO, edge[0][PIPE_WRITE]) ) {
			perror("attach");
			exit(-1);
		}
		multiplex(STDIN_FILENO, edge[2][PIPE_READ]);
		exit(0);
	default:
		break;
	}

				/* Duplicator */
	switch ( (node[2] = fork()) ) {
	case -1:
		perror("cannot fork");
		exit(-1);
	case 0:			/* child */
		if ( !attach(edge[1][PIPE_READ], STDOUT_FILENO) ) {
			perror("attach");
			exit(-1);
		}
		duplicate(STDOUT_FILENO, edge[2][PIPE_WRITE]);
		exit(0);
	default:
		break;
	}


					/* Command */
	switch ( (node[1] = fork()) ) {
	case -1:
		perror("cannot fork");
		exit(-1);
	case 0:			/* child */
		if ( !attach(edge[0][PIPE_READ], edge[1][PIPE_WRITE]) ) {
			perror("attach");
			exit(-1);
		}
		execl("/bin/sh", "/bin/sh", "-c", cmd, NULL);
		perror("execl failed");
		exit(-1);
	default:
		break;
	}

	child = wait(&retval);
	for (i=0; i<3; i++) {
		if ( child != node[i] ) {
			kill(node[i], SIGKILL);
		}
	}

	for (i=0; i<3; i++) {
		close(edge[i][PIPE_WRITE]);
		close(edge[i][PIPE_READ]);
	}
	
	return retval;
} /* buildgraph */

static void
multiplex(int fd1, int fd2)
{
	fd_set			rset;
	int			fd;
	char			buf[BUFLEN];
	int			len 	= 0;
	int			fdsel	= max(fd1, fd2) + 1;
	int			n;

	while ( 1 ) {
		FD_ZERO(&rset);
		FD_SET(fd1, &rset);
		FD_SET(fd2, &rset);

		for (n=select(fdsel, &rset, NULL, NULL, NULL); n; n--) {
			fd = 0;
			if ( FD_ISSET(fd1, &rset) ) {
				FD_CLR(fd1, &rset);
				fd = fd1;
			} else if ( FD_ISSET(fd2, &rset) ) {
				FD_CLR(fd2, &rset);
				fd = fd2;
			}
			if ( fd >= 0 ) {
				len = read(fd, buf, sizeof buf);
				if ( len > 0 ) {
					write(STDOUT_FILENO, buf, len);
				} if ( len < 0 ) {
					perror("read");
					return;
				}
			}
		}
	}
} /* multiplex */

static void
duplicate(int fd1, int fd2)
{
	char	buf[BUFLEN];
	int	len = 0;

	while ( len >= 0 ) {
		len = read(STDIN_FILENO, buf, sizeof buf);
		if ( len > 0 ) {
			write(fd1, buf, len);
			write(fd2, buf, len);
		}
	}
} /* duplicate */


static int
attach(int in, int out)
{
	if ( in != STDIN_FILENO ) {
		if ( dup2(in, STDIN_FILENO) != STDIN_FILENO ) {
			return 0;
		}
	}
	if ( out != STDOUT_FILENO ) {
		if ( dup2(out, STDOUT_FILENO) != STDOUT_FILENO ) {
			return 0;
		}
	}
	return 1;
} /* attach */


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


