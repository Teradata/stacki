#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <openssl/md5.h>

extern void logmsg(const char *, ...);

extern MD5_CTX	context;


static int
verify_md5(char *md5)
{
	int		i;
	unsigned char	digest[16];
	char		digest_str[64];

	/*
	 * get the digest for the file we just read, then make it a string
	 */
	if (MD5_Final(digest, &context) != 1) {
		logmsg("verify_md5:MD5_Final failed\n");
		return(0);
	}

	bzero(digest_str, sizeof(digest_str));

	for (i = 0; i < sizeof(digest) ; ++i) {
		sprintf(digest_str, "%s%02x", digest_str,
			(unsigned char)digest[i]);
	}

	if (strcmp(digest_str, md5) == 0) {
		return(1);
	}

	return(-1);
}

/*
 * check the MD5 for a file.
 *
 * return values:
 *
 *	 0 = no packages.md5 file or no entry in packages.md5 for the filename
 *	 1 = checksum passed
 *	-1 = checksum failed
 */
int
check_md5(char *filename)
{
	FILE	*file;
	int	retval;
	int	passed;
	char	digest[64];
	char	fname[1024];
	char	done;

	passed = 0;

	if ((file = fopen("/tmp/product/packages.md5", "r")) == NULL) {
		logmsg("check_md5:fopen:failed\n");
		return(passed);
	}

	done = 0;
	while (!done) {
		retval = fscanf(file, "%s %s", digest, fname);

		if (retval == 2) {
			if (strlen(filename) >= strlen(fname)) {
				/*
				 * check if the last part of the filename
				 * matches fname found in the packages.md5 file
				 */
				char *ptr = (char *)&filename[
					strlen(filename) - strlen(fname)];

				if (strcmp(fname, ptr) == 0) {
					if (verify_md5(digest) == 1) {
						logmsg("MD5 checksum passed for file %s\n", filename);
						passed = 1;
					} else {
						logmsg("MD5 checksum failed for file %s\n", filename);
						passed = -1;
					}

					done = 1;
					continue;
				}
			}
		} else if (retval == EOF) {
			done = 1;
			continue;
		}
	}

	fclose(file);
	return(passed);
}


