#include <stdio.h>
#include <string.h>
#include <strings.h>
#include <stdlib.h>
#include <time.h>
#include <errno.h>
#include <sys/time.h>
#include "tracker.h"

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/utsname.h>
#include <mysql/mysql.h>
#include <netdb.h>


static char builton[] = { "Built on: " __DATE__ " " __TIME__ };

extern int shuffle(peer_t *, uint16_t, char *);
extern char *getcoop(in_addr_t, char *);
extern void clear_dt_table_entry(in_addr_t);

#ifdef	WITH_MYSQL
extern char *gethostattr(char *, char *);
#endif

hash_table_t	*hash_table = NULL;

int
init_hash_table(int size)
{
	int		len;

	len = sizeof(hash_table_t) + (size * sizeof(hash_info_t));

	if ((hash_table = malloc(len)) == NULL) {
		perror("init_hash_table:malloc failed:");
		return(-1);
	}
	
	bzero(hash_table, len);
	hash_table->size = size;
	hash_table->head = 0;
	hash_table->tail = size - 1;

	return(0);
}

void
print_peers(hash_info_t *hashinfo)
{
	struct in_addr	in;
	int		i;

	fprintf(stderr, "print_peers:numpeers %d\n",  hashinfo->numpeers);

	for (i = 0 ; i < hashinfo->numpeers ; ++i) {
		in.s_addr = hashinfo->peers[i].ip;
		fprintf(stderr, "\t%s : %c\n", inet_ntoa(in), 
			(hashinfo->peers[i].state == DOWNLOADING ? 'd' : 'r'));
	}
}

void
print_hash_table()
{
	int	i;

	fprintf(stderr, "head: (%d)\n", hash_table->head);
	fprintf(stderr, "tail: (%d)\n", hash_table->tail);

	if (hash_table->head >= hash_table->tail) {
		for (i = hash_table->head - 1;
				(i > hash_table->tail) && (i >= 0) ; --i) {

			fprintf(stderr, "entry[%d] : hash (0x%lx)\n", i,
				hash_table->entry[i].hash);

			print_peers(&hash_table->entry[i]);
		}
	} else {
		for (i = hash_table->head - 1; i >= 0 ; --i) {
			fprintf(stderr, "entry[%d] : hash (0x%lx)\n", i,
				hash_table->entry[i].hash);

			print_peers(&hash_table->entry[i]);
		}

		for (i = (hash_table->size - 1) ;
				(i > hash_table->tail) && (i >= 0) ; --i) {

			fprintf(stderr, "entry[%d] : hash (0x%lx)\n", i,
				hash_table->entry[i].hash);

			print_peers(&hash_table->entry[i]);
		}
	}

	return;
}

void
verify_hash_table()
{
	int	i;

	print_hash_table();

	if (hash_table->head >= hash_table->tail) {
		for (i = hash_table->head - 1;
				(i > hash_table->tail) && (i >= 0) ; --i) {

			if (hash_table->entry[i].hash == 0) {
				fprintf(stderr, "verify_hash_table:1: error at entry %d\n", i);
				exit(-1);
			}
		}
	} else {
		for (i = hash_table->head - 1; i >= 0 ; --i) {
			if (hash_table->entry[i].hash == 0) {
				fprintf(stderr, "verify_hash_table:2: error at entry %d\n", i);
				exit(-1);
			}
		}

		for (i = (hash_table->size - 1) ;
				(i > hash_table->tail) && (i >= 0) ; --i) {

			if (hash_table->entry[i].hash == 0) {
				fprintf(stderr, "verify_hash_table:3: error at entry %d\n", i);
				exit(-1);
			}

		}
	}

	return;
}

/*
 * remove all free entries in between the head and the tail
 */
void
compact_hash_table()
{
	int	free_index = hash_table->head - 1;
	int	allocated_index;
	char	found, done;

#ifdef	DEBUG
	fprintf(stderr, "compact_hash_table:before\n\n");
	print_hash_table();
#endif

	while (1) {
		/*
		 * find a free slot
		 */
		found = 0;
		done = 0;
		while (!done) {
			if (free_index == hash_table->tail) {
				done = 1;
				continue;
			}

			if (free_index < 0) {
				free_index = hash_table->size - 1;
				continue;
			}

			if (hash_table->entry[free_index].hash == 0) {
				done = 1;
				found = 1;
				continue;
			}

			--free_index;
		}

		if (found == 0) {
			/*
			 * there are no free slots between head and tail
			 */
			return;
		}

		/*
		 * find the next allocated slot
		 */
		allocated_index = free_index - 1;
		found = 0;
		done = 0;

		while (!done) {
			if (allocated_index == hash_table->tail) {
				done = 1;
				continue;
			}

			if (allocated_index < 0) {
				allocated_index = hash_table->size - 1;
				continue;
			}

			if (hash_table->entry[allocated_index].hash != 0) {
				done = 1;
				found = 1;
				continue;
			}

			--allocated_index;
		}

		if (found == 0) {
			/*
			 * there are no allocated slots between free_index and
			 * tail
			 */
			return;
		}

		/*
		 * move the allocated slot to the free slot, then free the
		 * previous allocated slot
		 */
		hash_table->entry[free_index].hash =
			hash_table->entry[allocated_index].hash;
		hash_table->entry[free_index].numpeers =
			hash_table->entry[allocated_index].numpeers;
		hash_table->entry[free_index].peers =
			hash_table->entry[allocated_index].peers;

		hash_table->entry[allocated_index].hash = 0;
		hash_table->entry[allocated_index].numpeers = 0;
		hash_table->entry[allocated_index].peers = NULL;

		--free_index;
	}

#ifdef	DEBUG
	fprintf(stderr, "compact_hash_table:after\n\n");
	print_hash_table();
#endif

}

void
reclaim_free_entries()
{
	int	i;
	int	current_tail, current_head;

#ifdef	DEBUG
	fprintf(stderr,
		"reclaim_free_entries:head (%d), tail (%d), size (%d)\n",
		hash_table->head, hash_table->tail, hash_table->size);
#endif

	/*
	 * first, try to move the tail
	 */
	if (hash_table->tail > hash_table->head) {
		current_tail = hash_table->tail;

		for (i = current_tail + 1 ; i < hash_table->size &&
				hash_table->entry[i].hash == 0 ; ++i) {
			++hash_table->tail;
		}

		/*
	 	 * special case when the tail hits the end of the list
		 */
		if (hash_table->tail == hash_table->size - 1) {
			if ((hash_table->entry[0].hash == 0) && 
					(hash_table->head != 0)) {
				hash_table->tail = 0;
			}
		}
	}

	if (hash_table->tail < hash_table->head) {
		current_tail = hash_table->tail;

		for (i = current_tail + 1 ; i < hash_table->head &&
				hash_table->entry[i].hash == 0 ; ++i) {
			++hash_table->tail;
		}
	}

	/*
	 * now try to move the head
	 */
	if (hash_table->head < hash_table->tail) {
		current_head = hash_table->head;

		for (i = current_head - 1 ; i >= 0 &&
				hash_table->entry[i].hash == 0 ; --i) {
			--hash_table->head;
		}

		/*
		 * special case for when head hits the top of the list
		 */
		if ((hash_table->head == 0) &&
			(hash_table->entry[hash_table->size - 1].hash == 0)) {

			hash_table->head = hash_table->size - 1;
		}
	}

	if (hash_table->head > hash_table->tail) {
		current_head = hash_table->head;

		for (i = current_head - 1 ; i < hash_table->tail &&
				hash_table->entry[i].hash == 0 ; --i) {
			--hash_table->head;
		}
	}

#ifdef	DEBUG
	fprintf(stderr, "reclaim_free_entries:head (%d), tail (%d)\n",
		hash_table->head, hash_table->tail);
#endif
}

/*
 * 'size' is the number of new entries to be added to the table
 */
int
grow_hash_table(int size)
{
	uint32_t	oldsize = hash_table->size;
	uint32_t	newsize = size + hash_table->size;
	int		len;
	int		tailentries;

	len = sizeof(hash_table_t) + (newsize * sizeof(hash_info_t));

#ifdef	DEBUG
	fprintf(stderr, "grow_hash_table:enter:size (%d)\n", hash_table->size);
	fprintf(stderr, "grow_hash_table:enter:head (%d)\n", hash_table->head);
	fprintf(stderr, "grow_hash_table:enter:tail (%d)\n", hash_table->tail);

	fprintf(stderr, "grow_hash_table:before\n\n");
	print_hash_table();
#endif

	if ((hash_table = realloc(hash_table, len)) == NULL) {
		perror("grow_hash_table:realloc failed:");
		return(-1);
	}

	tailentries = oldsize - 1 - hash_table->tail;
#ifdef	DEBUG
	fprintf(stderr, "grow_hash_table:tailentries (%d)\n", tailentries);
#endif
	if (tailentries > 0) {
		/*
		 * if the tail is "not" pointing at the last entry of the
		 * old table, then we need to copy the bottom of the old
		 * table to the bottom of the new table
		 */
		memcpy(&hash_table->entry[newsize - tailentries],
			&hash_table->entry[hash_table->tail + 1],
			tailentries * sizeof(hash_info_t));
	}

	/*
	 * initialize the new entries
	 */
	bzero(&hash_table->entry[hash_table->head],
		(size + 1) * sizeof(hash_info_t));

	hash_table->size = newsize;
	hash_table->tail = hash_table->tail + size;

#ifdef	DEBUG
	fprintf(stderr, "grow_hash_table:exit:size (%d)\n", hash_table->size);
	fprintf(stderr, "grow_hash_table:exit:head (%d)\n", hash_table->head);
	fprintf(stderr, "grow_hash_table:exit:tail (%d)\n", hash_table->tail);

	fprintf(stderr, "grow_hash_table:after\n\n");
	print_hash_table();
#endif

#ifdef	DEBUG
	fprintf(stderr, "grow_hash_table:validate new free entries\n");
{
	int	i;

	for (i = hash_table->head; i <= hash_table->tail; ++i) {
		fprintf(stderr, "\tentry[%d] : hash (0x%llx)\n", i,
			hash_table->entry[i].hash);
		if (hash_table->entry[i].hash != 0) {
			fprintf(stderr, "grow_hash_table:validate fail\n");
			exit(-1);
		}
	}
}
#endif

	return(0);
}

hash_info_t *
newentry()
{
	int	index;
	
	index = hash_table->head;

	++hash_table->head;

	if (hash_table->head == hash_table->tail) {
		if (grow_hash_table(HASH_TABLE_ENTRIES) != 0) {
			fprintf(stderr, "newentry:grow_hash_table:failed\n");
			return(NULL);
		}
	}

	if (hash_table->head == hash_table->size) {
		hash_table->head = 0;
	}

	return(&hash_table->entry[index]);
}

int
addpeer(hash_info_t *hashinfo, peer_t *peer)
{
	if (hashinfo == NULL) {
		fprintf(stderr, "addpeer:hashinfo NULL\n");
		return(-1);
	}

#ifdef	DEBUG
{
	struct in_addr	in;

	in.s_addr = peer->ip;
	fprintf(stderr, "addpeer:adding peer (%s) for hash (0x%016llx)\n",
		inet_ntoa(in), hashinfo->hash);

	fprintf(stderr, "addpeer:before\n");
	print_peers(hashinfo);
}
#endif

	if (hashinfo->peers) {
		if ((hashinfo->peers = realloc(hashinfo->peers,
			(hashinfo->numpeers + 1) * sizeof(*peer))) == NULL) {

			fprintf(stderr, "addpeer:realloc failed\n");
			return(-1);
		}
	} else {
		if ((hashinfo->peers = malloc(sizeof(*peer))) == NULL) {
			fprintf(stderr, "addpeer:malloc failed\n");
			return(-1);
		}
	}

	memcpy(&hashinfo->peers[hashinfo->numpeers], peer, sizeof(*peer));
	++hashinfo->numpeers;

#ifdef	DEBUG
	fprintf(stderr, "addpeer:after\n");
	print_peers(hashinfo);
	fprintf(stderr, "\n");
#endif
		
	return(0);
}

hash_info_t *
getpeers(uint64_t hash, int *index)
{
	int	i;
	int	h = hash_table->head;
	int	found = -1;
#ifdef	TIMEIT
	struct timeval		start_time, end_time;
	unsigned long long	s, e;
#endif

#ifdef	TIMEIT
	gettimeofday(&start_time, NULL);
#endif

	if (h < hash_table->tail) {
		/*
		 * work down to entry 0, then reset the head (h) to the
		 * last entry of the table
		 */
		for (i = h - 1; i >= 0 ; --i) {
			if (hash_table->entry[i].hash == hash) {
				found = i;
				break;
			}
		}

		h = hash_table->size - 1;
	}

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	fprintf(stderr, "getpeers:svc time1: %lld\n", (e - s));
#endif

	if (found == -1) {
		/*
		 * we know head (h) is greater than tail
		 */
		for (i = h ; i >= hash_table->tail ; --i) {
			if (hash_table->entry[i].hash == hash) {
				found = i;
				break;
			}
		}
	}

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	fprintf(stderr, "getpeers:svc time2: %lld\n", (e - s));
#endif

	if (found != -1) {
#ifdef	DEBUG
		fprintf(stderr, "getpeers:hash (0x%016llx) found\n", hash);
#endif
		if (index != NULL) {
			*index = i;
		}

		return(&hash_table->entry[i]);
	}

	/*
	 * if we made it here, then the hash is not in the table
	 */
#ifdef	DEBUG
	fprintf(stderr, "getpeers:hash (0x%016llx) not found\n", hash);
#endif

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	fprintf(stderr, "getpeers:svc time3: %lld\n", (e - s));
#endif
	return(NULL);
}

hash_info_t *
getnextpeers(uint64_t hash, int *index)
{
	int	i;

#ifdef	DEBUG
	fprintf(stderr, "getnextpeers:hash (0x%llx), index (%d), head (%d), tail (%d)", hash, *index, hash_table->head, hash_table->tail);
#endif

	/*
	 * look from the current index to the end of the table (or stop
	 * when hit the head of the table).
	 */
	for (i = (*index) + 1 ; i < hash_table->size ; ++i) {
		if (i == hash_table->head) {
#ifdef	DEBUG
			fprintf(stderr, " return(NULL)\n");
#endif
			return(NULL);
		}

		if (hash_table->entry[i].hash != 0) {
			*index = i;
#ifdef	DEBUG
			fprintf(stderr, " return: index (%d), hash (0x%llx)\n",
				i, hash_table->entry[i].hash);
#endif
			return(&hash_table->entry[i]);
		}
	}

	/*
	 * now look from the bottom of the table to the head
	 */
	for (i = 0 ; i < hash_table->head ; ++i) {
		if (hash_table->entry[i].hash != 0) {
			*index = i;
#ifdef	DEBUG
			fprintf(stderr, " return: index (%d), hash (0x%llx)\n",
				i, hash_table->entry[i].hash);
#endif
			return(&hash_table->entry[i]);
		}
	}

#ifdef	DEBUG
	fprintf(stderr, " return(NULL)\n");
#endif
	return(NULL);
}

void
prep_peers(hash_info_t *hashinfo, tracker_info_t *respinfo,
	struct sockaddr_in *from_addr, char *found)
{
	int	numpeers;
	int	i;
	char	*coop;

	coop = getcoop(from_addr->sin_addr.s_addr, "coop");
	shuffle(hashinfo->peers, hashinfo->numpeers, coop);
	free(coop);

	/*
	 * copy the hash info into the response buffer
	 */
	respinfo->hash = hashinfo->hash;
	respinfo->numpeers = 0;

	numpeers = min(hashinfo->numpeers, PEERS_PER_PREDICTION);
	i = 0;

	while (respinfo->numpeers < numpeers) {
		/*
		 * don't copy in address of requestor
		 */
		if (hashinfo->peers[i].ip == from_addr->sin_addr.s_addr) {
			if (found != NULL) {
				*found = 1;
				hashinfo->peers[i].state = DOWNLOADING;
			}
			--numpeers;
			continue;
		}

		memcpy(&respinfo->peers[respinfo->numpeers], 
			&hashinfo->peers[i],
			sizeof(respinfo->peers[respinfo->numpeers]));

		++respinfo->numpeers;
		++i;
	}
}

void
avalanche_log(in_addr_t from, in_addr_t to, uint64_t hash)
{
	static int			mq = 0;
	static struct sockaddr_in	saddr;

	char		*src;
	char		*dst;
	char		msg[128];

	if ( ! mq ) {
		mq = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
		bzero(&saddr, sizeof saddr);
		saddr.sin_family	= AF_INET;
		saddr.sin_port		= htons(5000);
		saddr.sin_addr.s_addr	= htonl(INADDR_LOOPBACK);
	}

	src = strdup(inet_ntoa(*(struct in_addr *)&from));
	dst = strdup(inet_ntoa(*(struct in_addr *)&to));

	sprintf(msg, 
		"rawtracker { \"from\":\"%s\", \"to\":\"%s\", \"hash\":\"%lx\" }",
		src, dst, hash);

 	sendto(mq, msg, strlen(msg), 0, &saddr, sizeof saddr);

	free(src);
	free(dst);
}

void
dolookup(int sockfd, uint64_t hash, uint32_t seqno,
	struct sockaddr_in *from_addr)
{
	tracker_lookup_resp_t	*resp;
	tracker_info_t		*respinfo;
	hash_info_t		*hashinfo;
	hash_info_t		*predhashinfo;
	size_t			len;
	int			j;
	int			flags;
	int			index, next_index;
	char			found;
	char			buf[64*1024];

	resp = (tracker_lookup_resp_t *)buf;
	resp->header.op = LOOKUP;
	resp->header.seqno = seqno;

	/*
	 * keep a running count for the length of the data
	 */
	len = sizeof(tracker_lookup_resp_t);

	/*
	 * look up info for this hash
	 */
	respinfo = (tracker_info_t *)resp->info;
	respinfo->hash = hash;

	len += sizeof(tracker_info_t);

	/*
	 * always send back at least one hash, even if it is empty (i.e.,
	 * it has no peers.
	 */
	resp->numhashes = 1;

	found = 0;

	if ((hashinfo = getpeers(hash, &index)) != NULL) {
		/*
		 * shuffle the peers
		 */
		prep_peers(hashinfo, respinfo, from_addr, &found);

		if (respinfo->numpeers > 0) {
			avalanche_log(respinfo->peers[0].ip, from_addr->sin_addr.s_addr, hash);
		}

#ifdef	DEBUG
		fprintf(stderr,
			"resp info numpeers (%d)\n", respinfo->numpeers);
#endif

		len += (sizeof(respinfo->peers[0]) * respinfo->numpeers);

		respinfo = (tracker_info_t *)
			(&(respinfo->peers[respinfo->numpeers]));

		/*
		 * now get hash info for the "predicted" next file downloads
		 */
		next_index = index;
		for (j = 0 ; j < PREDICTIONS ; ++j) {
			if ((predhashinfo = getnextpeers(hash, &next_index))
					!= NULL) {

				if (index == next_index) {
					/*
					 * there are less than 'PREDICTIONS'
					 * number of valid hash entries and
					 * we've examined them all. break out
					 * of this loop.
					 */
					break;
				}

				prep_peers(predhashinfo, respinfo, from_addr,
					NULL);

				if (respinfo->numpeers > 0) {
					avalanche_log(respinfo->peers[0].ip,
						      from_addr->sin_addr.s_addr,
						      predhashinfo->hash);
				}
			} else {
				/*
				 * no more valid hashes
				 */
				break;
			}

			len += sizeof(tracker_info_t) +
				(sizeof(respinfo->peers[0]) *
					respinfo->numpeers);

			respinfo = (tracker_info_t *)
				(&(respinfo->peers[respinfo->numpeers]));

			++resp->numhashes;
		}

#ifdef	DEBUG
	fprintf(stderr, "len (%d)\n", (int)len);
#endif

	} else {
		/*
		 * this hash is not in the table, so let's add it.
		 */
		if ((hashinfo = newentry()) == NULL) {
			fprintf(stderr, "dolookup:newentry:failed\n");
			abort();
		}

		hashinfo->hash = hash;
		hashinfo->numpeers = 0;

		respinfo->numpeers = 0;

		avalanche_log(ntohl(INADDR_LOOPBACK), from_addr->sin_addr.s_addr, hash);
	}

	if (!found) {
		peer_t	newpeer;

		/*
		 * the client has made a 'lookup' request which means the client
		 * will soon be downloading the file. let's add this peer to
		 * the hash and mark this peer as 'downloading'.
		 */
		newpeer.ip = from_addr->sin_addr.s_addr;
		newpeer.state = DOWNLOADING;
#ifdef	DEBUG
		fprintf(stderr, "dolookup:calling addpeer\n");
#endif

		addpeer(hashinfo, &newpeer);
	}

#ifdef	DEBUG
	fprintf(stderr, "dolookup:numhashes (%d)\n", resp->numhashes);
#endif

	resp->header.length = len;

#ifdef	DEBUG
	fprintf(stderr, "send buf: ");
	dumpbuf((char *)resp, len);
#endif

	flags = 0;
	sendto(sockfd, buf, len, flags, (struct sockaddr *)from_addr,
		sizeof(*from_addr));

#ifdef	DEBUG
	fprintf(stderr, "dolookup:exit:hash (0x%llx)\n", hash);
#endif

	return;
}

void
register_hash(char *buf, struct sockaddr_in *from_addr)
{
	tracker_register_t	*req = (tracker_register_t *)buf;
	hash_info_t		*hashinfo;
	tracker_info_t		*reqinfo;
	uint16_t		numpeers;
	peer_t			dynamic_peers[1];
	peer_t			*peers;
	int			i, j, k;

	for (i = 0; i < req->numhashes; ++i) {
		reqinfo = &req->info[i];
#ifdef	LATER
		fprintf(stderr,
			"register_hash:enter:hash (0x%llx)\n", reqinfo->hash);
		fprintf(stderr, "register_hash:hash_table:before\n\n");
		print_hash_table();
#endif

		if (reqinfo->numpeers == 0) {
			/*
			 * no peer specified. dynamically determine
			 * the peer IP address from the host who
			 * sent us the message
			 */
			numpeers = 1;
			dynamic_peers[0].ip = from_addr->sin_addr.s_addr;
			peers = dynamic_peers;
		} else {
			numpeers = reqinfo->numpeers;
			peers = reqinfo->peers;
		}

#ifdef	DEBUG
		fprintf(stderr, "register_hash:numpeers:1 (0x%d)\n", numpeers);
#endif

		/*
		 * scan the list for this hash.
		 */
		if ((hashinfo = getpeers(reqinfo->hash, NULL)) != NULL) {
			/*
			 * this hash is already in the table, see if this peer
			 * is already in the list
			 */
			for (j = 0 ; j < numpeers ; ++j) {
				int	found = 0;
		
				for (k = 0 ; k < hashinfo->numpeers ; ++k) {
					if (peers[j].ip ==
							hashinfo->peers[k].ip) {
						found = 1;
						hashinfo->peers[k].state =
							READY;
						break;
					}
				}

				if (!found) {
					peers[j].state = READY;
#ifdef	DEBUG
					fprintf(stderr, "register_hash:calling addpeer:1\n");
#endif
					addpeer(hashinfo, &peers[j]);
				}
			}
		} else {
			/*
			 * if not, then add this hash to the end of the list
			 */
			if ((hashinfo = newentry()) == NULL) {
				fprintf(stderr,
					"register_hash:newentry:failed\n");
				abort();
			}

			hashinfo->hash = reqinfo->hash;
			hashinfo->numpeers = 0;

			for (j = 0 ; j < numpeers ; ++j) {
				peers[j].state = READY;
#ifdef	DEBUG
				fprintf(stderr,
					"register_hash:calling addpeer:2\n");
#endif
				addpeer(hashinfo, &peers[j]);
			}
		}
#ifdef	LATER
	fprintf(stderr, "register_hash:hash_table:after\n\n");
	print_hash_table();
#endif

#ifdef	DEBUG
	fprintf(stderr, "register_hash:exit:hash (0x%llx)\n", reqinfo->hash);
#endif
	}
}

void
removepeer(int index, peer_t *peer, char do_compact)
{
	hash_info_t	*hashinfo = &hash_table->entry[index];
	int		i, j;

#ifdef	DEBUG
{
	struct in_addr	in;

	in.s_addr = peer->ip;
	fprintf(stderr, "removepeer:removing peer (%s) for hash (0x%016llx)\n",
		inet_ntoa(in), hashinfo->hash);
}
#endif

	for (i = 0; i < hashinfo->numpeers; ++i) {
		if (hashinfo->peers[i].ip == peer->ip) {
			if (hashinfo->numpeers == 1) {
				/*
				 * do the easy case first
				 */
				free(hashinfo->peers);

				hashinfo->peers = NULL;
				hashinfo->hash = 0;
				hashinfo->numpeers = 0;

				if (do_compact) {
					compact_hash_table();
					reclaim_free_entries();
				}
			} else {
				/*
				 * remove the peer by compacting all subsequent
				 * peers
				 */
				for (j = i; j < hashinfo->numpeers - 1; ++j) {
					memcpy(&hashinfo->peers[j],
						&hashinfo->peers[j+1],
						sizeof(*peer));
				}

				/*
				 * zero out the last entry
				 */
				bzero(&hashinfo->peers[hashinfo->numpeers-1],
					sizeof(*peer));

				--hashinfo->numpeers;
			}

			break;
		}
	}

	return;
}

void
unregister_hash(char *buf, struct sockaddr_in *from_addr)
{
	tracker_unregister_t	*req = (tracker_unregister_t *)buf;
	peer_t			peer;
	int			index;
	int			i, j;

#ifdef	DEBUG
	fprintf(stderr, "unregister_hash:enter\n");
	fprintf(stderr, "unregister_hash:hash_table:before\n\n");
	print_hash_table();
#endif

	bzero(&peer, sizeof(peer));

	for (i = 0 ; i < req->numhashes ; ++i) {
		tracker_info_t	*info = &req->info[i];

		if (getpeers(info->hash, &index) != NULL) {
			for (j = 0 ; j < info->numpeers ; ++j) {
				peer.ip = info->peers[j].ip;
				removepeer(index, &peer, 1);
			}
		}
	}

#ifdef	DEBUG
	fprintf(stderr, "unregister_hash:hash_table:after\n\n");
	print_hash_table();
#endif
}

void
unregister_all(char *buf, struct sockaddr_in *from_addr)
{
	peer_t		peer;
	int		i;

#ifdef	DEBUG
	fprintf(stderr, "unregister_all:enter\n");
	fprintf(stderr, "unregister_all:hash_table:before\n\n");
	print_hash_table();
#endif

	peer.ip = from_addr->sin_addr.s_addr;

	if (hash_table->head >= hash_table->tail) {
		for (i = hash_table->head - 1;
				(i > hash_table->tail) && (i >= 0) ; --i) {
			removepeer(i, &peer, 0);
		}
	} else {
		for (i = hash_table->head - 1; i >= 0 ; --i) {
			removepeer(i, &peer, 0);
		}

		for (i = (hash_table->size - 1) ;
				(i > hash_table->tail) && (i >= 0) ; --i) {
			removepeer(i, &peer, 0);
		}
	}

	compact_hash_table();
	reclaim_free_entries();

	clear_dt_table_entry(peer.ip);

#ifdef	DEBUG
	fprintf(stderr, "unregister_all:hash_table:after\n\n");
	print_hash_table();
#endif

}

int
main()
{
	struct sockaddr_in	from_addr;
	socklen_t		from_addr_len;
	ssize_t			recvbytes;
	int			sockfd;
	char			buf[64*1024];
	char			done;
#ifdef	TIMEIT
#endif
	struct timeval		start_time, end_time;
	unsigned long long	s, e;


	if ((sockfd = init_tracker_comm(TRACKER_PORT)) < 0) {
		fprintf(stderr, "main:init_tracker_comm:failed\n");
		abort();
	}

	if (init_hash_table(HASH_TABLE_ENTRIES) != 0) {
		fprintf(stderr, "main:init_hash_table:failed\n");
		abort();
	}

#ifdef	DEBUG
	fprintf(stderr, "main:starting\n");
#endif

	/*
	 * needed for shuffle()
	 */
	srand(time(NULL));

	done = 0;
	while (!done) {
		from_addr_len = sizeof(from_addr);
		recvbytes = tracker_recv(sockfd, buf, sizeof(buf),
			(struct sockaddr *)&from_addr, &from_addr_len, NULL);

		if (recvbytes > 0) {
			tracker_header_t	*p;

			p = (tracker_header_t *)buf;

			gettimeofday(&start_time, NULL);
#ifdef	TIMEIT
#endif

			fprintf(stderr, "%lld : main:op %d from %s seqno %d\n",
				(long long int)start_time.tv_sec, p->op,
				inet_ntoa(from_addr.sin_addr), p->seqno);
#ifdef	DEBUG
#endif

			switch(p->op) {
			case LOOKUP:
				{
					tracker_lookup_req_t	*req;

					req = (tracker_lookup_req_t *)buf;
					dolookup(sockfd, req->hash, req->header.seqno, &from_addr);
				}
				break;

			case REGISTER:
				register_hash(buf, &from_addr);
				break;

			case UNREGISTER:
				unregister_hash(buf, &from_addr);
				break;

			case PEER_DONE:
				unregister_all(buf, &from_addr);
				break;

			case STOP_SERVER:
				fprintf(stderr,
					"Received 'STOP_SERVER' from (%s)\n",
					inet_ntoa(from_addr.sin_addr));
				exit(0);

			default:
				fprintf(stderr, "Unknown op (%d)\n", p->op);
				abort();
				break;
			}

			gettimeofday(&end_time, NULL);
			s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
			e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
			fprintf(stderr, "main:svc time: %lld\n", (e - s));
#ifdef	TIMEIT
#endif
#ifdef	LATER
			verify_hash_table();
#endif
		}
	}

	return(0);
}

