#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <strings.h>
#include <time.h>
#include <sys/time.h>
#include "tracker.h"

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

extern void logmsg(const char *, ...);

static uint32_t	seqno = 0;

int
lookup(int sockfd, in_addr_t *tracker, uint64_t hash, tracker_info_t **info)
{
	struct sockaddr_in	send_addr, recv_addr;
	struct timeval		timeout;
	socklen_t		recv_addr_len;
	tracker_lookup_req_t	req;
	ssize_t			recvbytes;
	int			retval;
	int			infosize;
	char			buf[64*1024];
	char			done;

	bzero(&send_addr, sizeof(send_addr));
	send_addr.sin_family = AF_INET;

#ifdef	DEBUG
#endif
	logmsg("lookup:hash 0x%llx seqno %d\n", hash, seqno);

	/*
	 * all 'tracker' ip addresses are already in network byte order
	 */
	send_addr.sin_addr.s_addr = *tracker;
	send_addr.sin_port = htons(TRACKER_PORT);

	bzero(&req, sizeof(req));
	req.header.op = LOOKUP;
	req.header.length = sizeof(tracker_lookup_req_t);
	req.header.seqno = seqno++;
	req.hash = hash;

	tracker_send(sockfd, (void *)&req, sizeof(req),
		(struct sockaddr *)&send_addr, sizeof(send_addr));

	recv_addr_len = sizeof(recv_addr);

#ifdef	DEBUG
	/*
	 * if we are in debug mode, increase the timeout because the tracker
	 * will be writing lots of debug output to disk, and the tracker could
	 * take longer than a second to respond
	 */
	timeout.tv_sec = 3;
	timeout.tv_usec = 0;
#else
	timeout.tv_sec = 2;
	timeout.tv_usec = 0;
#endif
	done = 0;
	while (!done) {
		recvbytes = tracker_recv(sockfd, (void *)buf, sizeof(buf),
			(struct sockaddr *)&recv_addr, &recv_addr_len,
			&timeout);


#ifdef	DEBUG
		logmsg("lookup:recvbytes (%ld)\n", recvbytes);
#endif

		if (recvbytes > 0) {
			tracker_lookup_resp_t	*resp;

			resp = (tracker_lookup_resp_t *)buf;

			/*
			 * validate the packet
			 */
			if (resp->header.op != LOOKUP) {
				logmsg("lookup:header op (%d) != (%d)\n",
					resp->header.op, LOOKUP);
				abort();
			}

			if (resp->header.seqno == req.header.seqno) {
				done = 1;
			} else{
				logmsg("lookup:seqno mismatch: got %d, exepcted %d\n", resp->header.seqno, req.header.seqno);
				continue;
			}

			/*
			 * make sure numhashes is reasonable
			 */
			if ((resp->numhashes < 0) || (resp->numhashes > 64)) {
				logmsg("lookup:numhashes (%d) is not between 0 and 64\n", resp->numhashes);
				abort();
			}

			/*
			 * get the size of the info structure
			 */
			infosize = resp->header.length -
				sizeof(tracker_lookup_resp_t);

			if ((*info = (tracker_info_t *)malloc(infosize)) ==
					NULL) {
				logmsg("lookup:malloc failed\n");
				abort();
			}

			memcpy(*info, resp->info, infosize);
			retval = resp->numhashes;
		} else {
			retval = 0;
			done = 1;
			fprintf(stderr,
				"lookup:tracker_recv:0 bytes seqno %d\n",
				req.header.seqno);
		}
	}

#ifdef	DEBUG
	logmsg("lookup:retval (%d)\n", retval);
#endif

	return(retval);
}

int
register_hash(int sockfd, in_addr_t *ip, uint32_t numhashes,
	tracker_info_t *info)
{
	struct sockaddr_in	send_addr;
	tracker_register_t	*req;
	int			len, infolen;
	int			i;

	bzero(&send_addr, sizeof(send_addr));
	send_addr.sin_family = AF_INET;

	/*
	 * the ip address is already in network byte order
	 */
	send_addr.sin_addr.s_addr = *ip;
	send_addr.sin_port = htons(TRACKER_PORT);

	infolen = 0;
	for (i = 0 ; i < numhashes ; ++i) {
		infolen += sizeof(tracker_info_t) +
			(info[i].numpeers * sizeof(*(info[i].peers)));
	}

	len = sizeof(tracker_register_t) + infolen;

	if ((req = (tracker_register_t *)malloc(len)) == NULL) {
		logmsg("register_hash:malloc failed\n");
		return(-1);
	}

	bzero(req, len);
	req->header.op = REGISTER;
	req->header.length = len;
	req->header.seqno = seqno++;

	req->numhashes = numhashes;

#ifdef	DEBUG
	logmsg("infolen (%d)\n", infolen);
#endif

	memcpy(req->info, info, infolen);

	tracker_send(sockfd, (void *)req, len, 
		(struct sockaddr *)&send_addr, sizeof(send_addr));

#ifdef	DEBUG
{
	struct in_addr		in;

	in.s_addr = *ip;
	logmsg("register: registered hash (0x%016llx) with tracker (%s)\n",
		info->hash, inet_ntoa(in));
}
#endif

	free(req);
	return(0);
}

int
unregister_hash(int sockfd, in_addr_t *ip, uint32_t numhashes,
	tracker_info_t *info)
{
	struct sockaddr_in	send_addr;
	tracker_unregister_t	*req;
	int			len, infolen;
	int			i;

	bzero(&send_addr, sizeof(send_addr));
	send_addr.sin_family = AF_INET;

	/*
	 * the ip address is already in network byte order
	 */
	send_addr.sin_addr.s_addr = *ip;
	send_addr.sin_port = htons(TRACKER_PORT);

	infolen = 0;
	for (i = 0 ; i < numhashes ; ++i) {
		infolen += sizeof(tracker_info_t) +
			(info[i].numpeers * sizeof(*(info[i].peers)));
	}

	len = sizeof(tracker_unregister_t) + infolen;

	if ((req = (tracker_unregister_t *)malloc(len)) == NULL) {
		logmsg("register_hash:malloc failed\n");
		return(-1);
	}

	bzero(req, len);
	req->header.op = UNREGISTER;
	req->header.length = len;
	req->header.seqno = seqno++;

	req->numhashes = numhashes;

#ifdef	DEBUG
	logmsg("infolen (%d), numhashes (%d)\n", infolen, numhashes);
#endif

	memcpy(req->info, info, infolen);

	tracker_send(sockfd, (void *)req, len, 
		(struct sockaddr *)&send_addr, sizeof(send_addr));

#ifdef	LATER
{
	struct in_addr		in;

	in.s_addr = *ip;
	logmsg("unregister_hash: unregistered hash (0x%016llx) with tracker (%s)\n",
		info->hash, inet_ntoa(in));
}
#endif

	free(req);
	return(0);
}

int
init(uint16_t *num_trackers, char *trackers_url, in_addr_t *trackers,
	uint16_t *maxpeers, char *pkg_servers_url, uint16_t *num_pkg_servers,
	in_addr_t *pkg_servers)
{
	char	*p, *q;
	char	done;

	/*
	 * the list of tracker(s)
	 */
	*num_trackers = 0;
	q = trackers_url;
	done = 0;
	while (!done) {
		if ((p = strchr(q, ',')) == NULL) {
			done = 1;
		} else {
			*p = '\0';
		}

		trackers[(*num_trackers)] = inet_addr(q);
		q = p + 1;

		++(*num_trackers);
		if (*num_trackers == MAX_TRACKERS) {
			break;
		}
	}

	/*
	 * set the maximum number of peers that should be registered with
	 * the tracker
	 */
	*maxpeers = 10;

	/*
	 * the list of package servers. if i can't get a package from a
	 * peer, then these are the servers that *always* have the package
	 */
	*num_pkg_servers = 0;
	q = pkg_servers_url;
	done = 0;
	while (!done) {
		if ((p = strchr(q, ',')) == NULL) {
			done = 1;
		} else {
			*p = '\0';
		}

		pkg_servers[(*num_pkg_servers)] = inet_addr(q);
		q = p + 1;

		++(*num_pkg_servers);
		if (*num_pkg_servers == MAX_PKG_SERVERS) {
			break;
		}
	}

	return(0);
}

int
send_msg(int sockfd, in_addr_t *ip, uint16_t op)
{
	struct sockaddr_in	send_addr;
	tracker_header_t	req;
	int			len;

	bzero(&send_addr, sizeof(send_addr));
	send_addr.sin_family = AF_INET;

	/*
	 * the ip address is already in network byte order
	 */
	send_addr.sin_addr.s_addr = *ip;
	send_addr.sin_port = htons(TRACKER_PORT);

	len = sizeof(req);

	bzero(&req, len);
	req.op = op;
	req.length = len;
	req.seqno = seqno++;

	tracker_send(sockfd, (void *)&req, len, 
		(struct sockaddr *)&send_addr, sizeof(send_addr));

	return(0);
}

