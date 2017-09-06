#include <stdint.h>
#include <netinet/in.h>

/*
 * hard-coded stuff
 */
#define	TRACKER_PORT		9632
#define	PREDICTIONS		10
#define	PEERS_PER_PREDICTION	3
#define DOWNLOAD_PORT		80
#define MAX_TRACKERS		32
#define MAX_PKG_SERVERS		32

/*
 * don't know why this isn't in a standard include file
 */
#define	min(a, b)	((a) < (b) ? (a) : (b))

/*
 * message structures
 */

typedef struct {
	uint16_t	op;
	uint16_t	length;
	uint32_t	seqno;
} tracker_header_t;

typedef struct {
	in_addr_t	ip;
	char		state;
} peer_t;

/*
 * tracker message types
 */
#define	LOOKUP		1
#define	REGISTER	2
#define	UNREGISTER	3
#define	PEER_DONE	4
#define	STOP_SERVER	5

/*
 * tracker 'states'
 */
#define	DOWNLOADING	1
#define	READY		2

/*
 * LOOKUP messages
 */
typedef struct {
	tracker_header_t	header;
	uint64_t		hash;
} tracker_lookup_req_t;

typedef struct {
	uint64_t	hash;
	uint16_t	numpeers;
	char		pad[6];		/* align on 64-bit boundary */
	peer_t		peers[0];
} tracker_info_t;

/*
 * hash_info_t is very similar to tracker_info_t. the main reason i'm not
 * using tracker_info_t in the hash table is because the 'peers[0]' structure
 * above doesn't not allow us to dynamically assign storage to 'peers' with
 * malloc() and realloc().
 */
typedef struct {
	uint64_t	hash;
	uint16_t	numpeers;
	char		pad[6];		/* align on 64-bit boundary */
	peer_t		*peers;
} hash_info_t;

typedef struct {
	tracker_header_t	header;
	uint32_t		numhashes;
	char			pad[4];		/* 64-bit alignment */
	tracker_info_t		info[0];
} tracker_lookup_resp_t;


/*
 * REGISTER messages
 */

/*
 * this is flexible enough to be able to register multiple files (hashes) or
 * register multiple files for multiple other peers
 */
typedef struct {
	tracker_header_t	header;
	uint32_t		numhashes;
	char			pad[4];		/* 64-bit alignment */
	tracker_info_t		info[0];
} tracker_register_t;

/* there is no response to a 'register' message */

/*
 * UNREGISTER messages
 */

/*
 * this is flexible enough to be able to unregister multiple files (hashes) or
 * unregister multiple files for multiple other peers
 */
typedef struct {
	tracker_header_t	header;
	uint32_t		numhashes;
	char			pad[4];		/* 64-bit alignment */
	tracker_info_t		info[0];
} tracker_unregister_t;

typedef struct {
	tracker_header_t	header;
} tracker_unregister_resp_t;

/*
 * hash table to hold the order in which files are requested
 */
#define	HASH_TABLE_ENTRIES	1024

typedef struct {
	int		head;
	int		tail;
	uint32_t	size;
	hash_info_t	entry[0];
} hash_table_t;

/*
 * downloads timestamp table.
 *
 * this table keeps track of the last time this server 'assigned' another
 * host as a download source for a specific hash.
 */

#define	DT_TABLE_ENTRIES	1024

typedef struct {
	in_addr_t		host;
	unsigned long long	timestamp;	/* gettimeofday in usecs */
	char			*coop;		/* coop group */
} download_timestamp_t;

typedef	struct {
	uint32_t		size;
	download_timestamp_t	entry[0];
} dt_table_t;

typedef struct {
	peer_t			peer;
	unsigned long long	timestamp;
	char			*coop;
} peer_timestamp_t;

/*
 * prototypes
 */
extern uint64_t hashit(char *);
extern int tracker_send(int, void *, size_t, struct sockaddr *, socklen_t);
extern ssize_t tracker_recv(int, void *, size_t, struct sockaddr *,
	socklen_t *, struct timeval *);
extern int init_tracker_comm(int);
extern void dumpbuf(char *, int);
