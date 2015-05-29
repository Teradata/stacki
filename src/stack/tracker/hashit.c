#include <stdio.h>
#include <strings.h>
#include <stdlib.h>
#include "tracker.h"

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

static char builton[] = { "Built on: " __DATE__ " " __TIME__ };

extern uint64_t hashit(char *);

int
main(int argc, char **argv)
{
	uint64_t	hash;

	if (argc != 2) {
		fprintf(stderr, "usage: %s <filename>\n", argv[0]);
		exit(-1);
	}

	hash = hashit(argv[1]);
	printf("0x%016llx %s\n", hash, argv[1]);
}
