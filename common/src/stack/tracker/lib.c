#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <strings.h>
#include <errno.h>
#include <unistd.h>
#include <netinet/in.h>
#include <sys/time.h>
#include "tracker.h"

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

void
logmsg(const char *fmt, ...)
{
	FILE	*file;
	va_list argptr;

	if ((file = fopen("/tmp/tracker-client.debug", "a+")) != NULL) {
		va_start(argptr, fmt);
		vfprintf(file, fmt, argptr);
		va_end(argptr);

		fclose(file);
	}

	return;
}

uint64_t
hashit(char *ptr)
{
	uint64_t	hash = 0;
	int		c;

	/*
	 * SDBM hash function
	 */

	while ((c = *ptr++) != '\0') {
		hash = c + (hash << 6) + (hash << 16) - hash;
	}

	return hash;
}

void
dumpbuf(char *buf, int len)
{
	int	i;

	for (i = 0; i < len; ++i) {
		fprintf(stderr, "%02x ", (unsigned char)buf[i]);
	}
	fprintf(stderr, "\n");
}

int
tracker_send(int sockfd, void *buf, size_t len, struct sockaddr *to,
	socklen_t tolen)
{
	int	flags = 0;

#ifdef	DEBUG
	fprintf(stderr, "send buf: ");
	dumpbuf(buf, len);
#endif

	if (sendto(sockfd, buf, len, flags, (struct sockaddr *)to, tolen) < 0){
		logmsg("tracker_send:sendto failed:errno (%d)\n", errno);
	}

	return(0);
}

ssize_t
tracker_recv(int sockfd, void *buf, size_t len, struct sockaddr *from,
	socklen_t *fromlen, struct timeval *timeout)
{
	ssize_t	size = 0;
	int	flags = 0;
	int	readit = 0;
	int	retval;

	if (timeout) {
#ifdef	TIMEIT
#endif
		struct timeval	start_time, end_time;
		long long	s, e, timeleft;
		fd_set		sockfds;

		FD_ZERO(&sockfds);
		FD_SET(sockfd, &sockfds);

		gettimeofday(&start_time, NULL);

		timeleft = (timeout->tv_sec * 1000000) + timeout->tv_usec;
		while (timeleft) {
			if ((timeout->tv_sec) == 0 && (timeout->tv_usec == 0)) {
				break;
			}

			retval = select(sockfd+1, &sockfds, NULL, NULL,
				timeout);

			if ((retval > 0) && (FD_ISSET(sockfd, &sockfds))) {
				readit = 1;
				break;
			} else if (retval < 0) {
				/*
				 * an error occurred
				 */
				logmsg("tracker_recv:select:error:errno %d\n",
					errno);
			} else {
				logmsg("tracker_recv:timeout\n");
				break;
			}

			gettimeofday(&end_time, NULL);
			s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
			e = (end_time.tv_sec * 1000000) + end_time.tv_usec;

			timeleft -= (e - s);
		}
#ifdef	TIMEIT
#endif
		gettimeofday(&end_time, NULL);
		s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
		e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
		logmsg("tracker_recv:svc time: %lld usec\n", (e - s));
	} else {
		readit = 1;
	}

	if (readit) {
		size = recvfrom(sockfd, buf, len, flags, from, fromlen);
	}
	
#ifdef	DEBUG
	if (size > 0) {
		fprintf(stderr, "recv buf: ");
		dumpbuf(buf, size);
	}
#endif

	return(size);
}

int
init_tracker_comm(int port)
{
	struct sockaddr_in	client_addr;
	int			sockfd;

	if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
		perror("init_tracker_comm:socket failed:");
		return(-1);
	}

	/*
	 * bind the socket so we can send from it
	 */
	bzero(&client_addr, sizeof(client_addr));
	client_addr.sin_family = AF_INET;
	client_addr.sin_addr.s_addr = htonl(INADDR_ANY);
	client_addr.sin_port = htons(port);

	if (bind(sockfd, (struct sockaddr *)&client_addr,
			sizeof(client_addr)) < 0) {
                perror("init_tracker_comm:bind failed:");
		close(sockfd);
                return(-1);
	}

	return(sockfd);
}
