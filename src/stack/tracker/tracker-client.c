/*
 * @SI_Copyright@
 *                             www.stacki.com
 *                                  v3.1
 * 
 *      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
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
 * 	 "This product includes software developed by StackIQ" 
 *  
 * 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
 * neither the name or logo of this software nor the names of its
 * authors may be used to endorse or promote products derived from this
 * software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
 * BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 * BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
 * OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
 * IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * @SI_Copyright@
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
 */

#include <stdio.h>
#include <stdarg.h>
#include <errno.h>
#include <string.h>
#include <strings.h>
#include <stdlib.h>
#include <stdint.h>
#include <limits.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <curl/curl.h>
#include <httpd/httpd.h>
#include <netinet/in.h>
#include "tracker.h"
#include "fcgi_stdio.h"
#include <sys/socket.h>
#include <arpa/inet.h>
#include <libgen.h>
#include <openssl/md5.h>

static char builton[] = { "Built on: " __DATE__ " " __TIME__ };

extern int init(uint16_t *, char *, in_addr_t *, uint16_t *, char *, uint16_t *,
	in_addr_t *);
extern int lookup(int, in_addr_t *, uint64_t, tracker_info_t **);
extern int register_hash(int, in_addr_t *, uint32_t, tracker_info_t *);
extern void logmsg(const char *, ...);
extern int send_msg(int, in_addr_t *, uint16_t);
extern int check_md5(char *);

extern int unregister_hash(int sockfd, in_addr_t *ip, uint32_t numhashes, tracker_info_t *info);

int	status = HTTP_OK;
MD5_CTX	context;


int
getargs(char *forminfo, char *filename)
{
	char	*ptr;

	/*
	 * help out sscanf by putting in a blank for '&'
	 */
	while (1) {
		if ((ptr = strchr(forminfo, '&')) == NULL) {
			break;
		}

		*ptr = ' ';
	}

	if (sscanf(forminfo, "filename=%4095s", filename) != 1) {
		/*
		 * XXX - log an error
		 */
		return(-1);
	}

	return(0);
}

size_t
doheaders(void *ptr, size_t size, size_t nmemb, void *stream)
{
	int	httpstatus;

	/*
	 * look for HTTP status code. if it is not 200, then set the status
	 * to -1 (this tells us not to output any data).
	 */
	if ((status >= HTTP_OK) && (status <= HTTP_MULTI_STATUS)) {
		if (sscanf(ptr, "HTTP/1.1 %d", &httpstatus) == 1) {
			status = httpstatus;
		}
	}

	return(size * nmemb);
}

size_t
dobody(void *ptr, size_t size, size_t nmemb, void *stream)
{
	if ((status >= HTTP_OK) && (status <= HTTP_MULTI_STATUS)) {
		fwrite(ptr, size, nmemb, stream);

		if (MD5_Update(&context, ptr, size * nmemb) != 1) {
			logmsg("dobody:MD5_Update failed\n");
		}
	}

	return(size * nmemb);
}

void
senderror(int http_error_code, char *msg, int other_error_code)
{
	/*
	 * HTTP/1.1 <errorcode> <error name>
	 *	
	 *	e.g., "HTTP/1.1 404 Not Found"
	 *	
	 */
        printf("HTTP/1.1 %d\n", http_error_code);

        printf("Content-type: text/plain\n");
        printf("Status: %d\n\n", http_error_code);
        printf("%s\n", msg);
        printf("other error code (%d)\n", other_error_code);
}

int
makeurl(char *header, char *filename, char *serverip, char *url,
	int url_max_size)
{
	int	length;

	/*
	 * +2 is for null terminator and (potential) added '/' character
	 */
	length = strlen(header) + strlen(serverip) + strlen(filename) + 2;

	if (length > url_max_size) {
		return(-1);
	}

	sprintf(url, "%s%s", header, serverip);

	if (filename[0] != '/') {
		sprintf(url, "%s/", url);
	}

	sprintf(url, "%s%s", url, filename);

	return(0);
}

void
do_sendfile(char *filename, char *range)
{
	printf("Content-Type: application/octet-stream\n");
	printf("Content-Length: %d\n", strlen(filename));
	printf("X-Sendfile: %s\n", filename);
	printf("\n");
}

int
outputfile(char *filename, char *range)
{
	struct stat	statbuf;
	off_t		offset;
	size_t		lastbyte;
	size_t		totalbytes;
	size_t		bytesread;
	char		done;
	char		buf[128*1024];
	size_t		count;
	int		fd;

	/*
	 * make sure the file exists
	 */
	if (stat(filename, &statbuf) != 0) {
		return(-1);
	}

	/*
	 * if a range is supplied, then we need to calculate the offset
	 * and total number of bytes to read
	 */
	if (range != NULL) {

		/*
		 * there are three cases:
		 *
		 *	1) there is no 'offset' supplied. this means read from
		 *	   the beginning of the file (offset 0).
		 *
		 *	2) there is no 'last byte' supplied. this means read
		 *	   to the end of the file
		 *
		 *	3) both 'offset and 'last byte' are supplied.
		 */
		if (range[0] == '-') {
			/*
			 * case 1
			 */
			sscanf(range, "-%ld", &lastbyte);
			offset = 0;
		} else if (range[strlen(range) - 1] == '-') {
			/*
			 * case 2
			 */
			sscanf(range, "%ld-", &offset);
			lastbyte = statbuf.st_size;
		} else {
			/*
			 * case 3
			 */
			sscanf(range, "%ld-%ld", &offset, &lastbyte);
		}

		totalbytes = (lastbyte - offset) + 1;

	} else {
		offset = 0;
		totalbytes = statbuf.st_size;
	}

	if ((fd = open(filename, O_RDONLY)) < 0) {
		logmsg("outputfile:open failed:errno (%d)\n", errno);
		return(-1);
	}

	if (offset > 0) {
		int	s;

		if ((s = lseek(fd, offset, SEEK_SET)) < 0) {
			logmsg("outputfile:lseek failed:errno (%d)\n", errno);
			logmsg("outputfile:lseek failed:s (%d)\n", s);
			close(fd);
			return(-1);
		}
	}

	/*
	 * output the HTTP headers
	 */
	if (range != NULL) {
		printf("HTTP/1.1 %d\n", HTTP_PARTIAL_CONTENT);
	} else {
		printf("HTTP/1.1 %d\n", status);
	}

	printf("Content-Type: application/octet-stream\n");
	printf("Content-Length: %d\n", (int)totalbytes);
	printf("\n");

	bytesread = 0;
	done = 0;

#ifdef	DEBUG
	logmsg("outputfile:filename (%s)\n", filename);
#endif

	while (!done) {
		ssize_t	i;

		if ((sizeof(buf) + bytesread) > totalbytes) {
			count = totalbytes - bytesread;
		} else {
			count = sizeof(buf);
		}

		if ((i = read(fd, buf, count)) < 0) {
			logmsg("outputfile:read failed: errno (%d)\n", errno);
			done = 1;
			continue;
		}

		/*
		 * output the buffer on stdout
		 */
		fwrite(buf, i, 1, stdout);

		bytesread += i;

		if (bytesread >= totalbytes) {
			done = 1;
		}
	}
	fflush(stdout);

	close(fd);
	return(0);
}

unsigned long long	curltime;

int
downloadfile(CURL *curlhandle, char *url, char *range)
{
	CURLcode		curlcode;
	int			retval;
#ifdef	TIMEIT
	struct timeval		start_time, end_time;
	unsigned long long	s, e;
#endif

	if ((curlcode = curl_easy_setopt(curlhandle, CURLOPT_URL, url)) !=
			CURLE_OK) {
		logmsg("downloadfile:curl_easy_setopt():failed:(%d)\n",
			curlcode);
		return(-1);
	}

#ifdef	DEBUG
	logmsg("URL : ");
	logmsg(url);
	logmsg("\n");
#endif

	if ((curlcode = curl_easy_setopt(curlhandle, CURLOPT_RANGE,
			range)) != CURLE_OK) {
		logmsg("downloadfile:curl_easy_setopt():failed:(%d)\n",
				curlcode);
		return(-1);
	}

#ifdef	TIMEIT
	gettimeofday(&start_time, NULL);
#endif

	if (MD5_Init(&context) != 1) {
		fprintf(stderr, "MD5_Init failed\n");
		exit(-1);
	}

	if ((curlcode = curl_easy_perform(curlhandle)) != CURLE_OK) {
		logmsg("downloadfile:curl_easy_perform():failed:(%d)\n",
			curlcode);
		return(-1);
	}

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("downloadfile:svc time: %lld usec:url %s\n", (e - s), url);
	curltime = e - s;
#endif

	/*
	 * if this is not a range request, then do an MD5 checksum of the file
	 */
	if (range == NULL) {
		retval = check_md5(url);

		/*
		 * check_md5 returns:
		 *
		 *	0 - the filename is not found in the packages.md5 file
		 *
		 *	1 - checksum passed
		 *
		 *	-1 - checksum failed
		 */
		if (retval == -1) {
			return(-1);
		}
	}

	return(0);
}

int
createdir(char *path)
{
	struct stat	buf;
	char		*ptr;
	char		*lastptr;
	char		done = 0;

	if (strlen(path) == 0)
		return(0);

	if (path[0] != '/') {
		return(0);
	}

	lastptr = &path[1];

	while (!done) {
		if ((ptr = index(lastptr, '/')) == NULL) {
			done = 1;
			continue;
		}

		*ptr = '\0';

		if (stat(path, &buf) != 0) {
			if (mkdir(path, 0755) != 0) {
				return(-1);
			}
		}

		*ptr = '/';

		lastptr = ptr + 1;
		if (lastptr >= (path + strlen(path))) {
			done = 1;
		}
	}

	/*
	 * we've created all the parent directories, now create the
	 * last directory
	 */
	if (mkdir(path, 0755) != 0) {
		return(-1);
	}

	return(0);
}

int
getlocal(char *filename, char *range)
{
	struct stat	buf;

	if (stat(filename, &buf) == 0) {

#ifdef	DEBUG
		logmsg("getlocal:file (%s)\n", filename);
#endif

		status = HTTP_OK;

		if (outputfile(filename, range) != 0) {
			logmsg("outputfile():failed:(%d)\n", errno);
			return(-1);
		}
	} else {
		return(-1);
	}

	return(0);
}


void
step()
{
	struct stat	buf;

	while (stat("/tmp/yo", &buf) == 0) {
		sleep(1);
	}
}

char *fromip;

int
getremote(char *filename, peer_t *peer, char *range, CURL *curlhandle)
{
#ifdef	TIMEIT
	struct timeval		start_time, end_time;
	unsigned long long	s, e;
#endif
	CURLcode	curlcode;
	struct in_addr	in;
	struct stat	buf;
	FILE		*file;
	useconds_t	stall;
	char		*tempfilename;
	char		*dirfile, *basefile;
	char		url[PATH_MAX];
	char		*dir;
	char		*ptr;

#ifdef	TIMEIT
	gettimeofday(&start_time, NULL);
#endif

	in.s_addr = peer->ip;

#ifdef	DEBUG
	logmsg("getremote: get file (%s) from (%s)\n", filename, inet_ntoa(in));
#endif

	status = HTTP_OK;

	/*
	 * we know the file is not on the local hard disk (because getlocal()
	 * is called before this function), so try to download the file
	 * from a peer
	 */

	/*
	 * first, let's see if the file systems have been formatted. if
	 * so, then copy over all the files that were downloaded in the
	 * first part of the installation (e.g., stage2.img, product.img)
	 * and set up a symbolic link from the ramdisk area to the disk.
	 */

	if (stat("/mnt/sysimage", &buf) == 0) {
		if (stat("/mnt/sysimage/install", &buf) != 0) {
			if (stat("/install", &buf) == 0) {
				system("/usr/bin/cp -R /install /mnt/sysimage");
				system("/usr/bin/rm -rf /install");
			} else {
				/*
				 * /install doesn't exist on the ramdisk, so
				 * just create a directory on the hard disk
				 */
				mkdir("/mnt/sysimage/install", 0755);
			}
			symlink("/mnt/sysimage/install", "/install");
		}
	}

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("getremote:svc time1: %lld usec\n", (e - s));
#endif

	/*
	 * make sure the destination directory exists
	 */
	if ((dir = strdup(filename)) != NULL) {
		if ((ptr = rindex(dir, '/')) != NULL) {
			*ptr = '\0';
			if (stat(dir, &buf) != 0) {
				createdir(dir);
			}
		}

		free(dir);
	}

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("getremote:svc time2: %lld usec\n", (e - s));
#endif

	if ((dirfile = strdup(filename)) == NULL) {
		logmsg("getremote:strdup failed:errno (%d)\n", errno);
		return(-1);
	}

	if ((basefile = strdup(filename)) == NULL) {
		logmsg("getremote:strdup failed:errno (%d)\n", errno);
		return(-1);
	}

	if ((tempfilename = tempnam(dirname(dirfile), basename(basefile))) ==
			NULL) {
		free(dirfile);
		free(basefile);
		logmsg("getremote:tempnam():failed\n");
		return(-1);
	}

	free(dirfile);
	free(basefile);

	/*
	 * make a 'http://' url and get the file.
	 */
	if ((file = fopen(tempfilename, "w")) == NULL) {
		logmsg("getremote:fopen():failed\n");
		free(tempfilename);
		return(-1);
	}

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("getremote:svc time3: %lld usec\n", (e - s));
#endif

	/*
	 * tell curl to save it to disk (save it to the file pointed
	 * to by 'file'
	 */
	if ((curlcode = curl_easy_setopt(curlhandle, CURLOPT_WRITEDATA,
			file)) != CURLE_OK) {
		logmsg("getremote:curl_easy_setopt():failed:(%d)\n", curlcode);
		free(tempfilename);
		return(-1);
	}

	if (makeurl("http://", filename, inet_ntoa(in), url, sizeof(url)) != 0){
		logmsg("getremote:makeurl():failed:(%d)", errno);
		free(tempfilename);
		return(-1);
	}

	if (fromip != NULL) {
		free(fromip);
	}
	fromip = strdup(inet_ntoa(in));

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("getremote:svc time4: %lld usec\n", (e - s));
#endif

	stall = 10000;

	while (stall < 1000000) {
		if (downloadfile(curlhandle, url, NULL) < 0) {
			status = HTTP_NOT_FOUND;
		}
#ifdef	DEBUG
		logmsg("getremote:download status %d : stall %d\n",
			status, stall);
#endif

		if ((status >= HTTP_OK) && (status <= HTTP_MULTI_STATUS)) {
			/*
			 * success. break out of loop
			 */
			break;
		} else {
			logmsg("getremote:downloadfile:failed:url %s\n", url);

			if (peer->state == DOWNLOADING) {
				stall *= 10;
				usleep(stall);	
			} else {
				/*
				 * don't return on failure here. we still need
				 * to do some cleanup
				 */
				status = HTTP_NOT_FOUND;
				break;
			}
		}
	}

	fclose(file);

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("getremote:svc time5: %lld usec\n", (e - s));
#endif

	/*
	 * we downloaded the file from a peer, so read it and output it
	 * to stdout
	 */
	if ((status >= HTTP_OK) && (status <= HTTP_MULTI_STATUS)) {
		/*
		 * now do an atomic move
		 */
		if (rename(tempfilename, filename) < 0) {
			logmsg("getremote:rename():failed:(%d)\n", errno);
			free(tempfilename);
			return(-1);
		}
		
		if (outputfile(filename, range) != 0) {
			logmsg("getremote:outputfile():failed:(%d)\n", errno);
			free(tempfilename);
			return(-1);
		}
	} else {
		/*
		 * on a failure, a zero-byte length file will be
		 * left on the disk -- this is because of the fopen().
		 * remove this zero-length file.
		 */
		unlink(filename);
		unlink(tempfilename);
		free(tempfilename);
		return(-1);	
	}

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("getremote:svc time6: %lld usec\n", (e - s));
#endif

	free(tempfilename);
	return(0);
}

tracker_info_t	*predictions = NULL;
int		predictions_size = 0;

void
save_prediction_info(tracker_info_t *infoptr, int info_count)
{
	tracker_info_t	*infoptr_first_entry;
	int		i, len, totalsize;

	/*
	 * the first entry in the tracker info is the entry that we
	 * explicitly asked for. all remaining entries are the predictions.
	 */
	if ((info_count <= 1) || (infoptr == NULL)) {
		return;
	}

	/*
	 * skip the first entry
	 */
	infoptr = (tracker_info_t *)((char *)infoptr + sizeof(tracker_info_t) +
		(sizeof(infoptr->peers[0]) * infoptr->numpeers));
	infoptr_first_entry = infoptr;

#ifdef	DEBUG
	logmsg("save_prediction_info:info_count (%d)\n", info_count);
#endif

	/*
	 * first, get the size of the entries
	 */
	totalsize = 0;
	for (i = 1 ; i < info_count ; ++i) {

#ifdef	DEBUG
		logmsg("prediction info\n");
		logmsg("info:hash (0x%llx)\n", infoptr->hash);
		logmsg("info:numpeers (%d)\n", infoptr->numpeers);
{
		int	j;

		logmsg("info:peers:\n");

		for (j = 0 ; j < infoptr->numpeers; ++j) {
			struct in_addr	in;

			in.s_addr = infoptr->peers[j].ip;
			logmsg("\t%s\n", inet_ntoa(in));
		}
}
#endif
		
		len = sizeof(tracker_info_t) +
			(sizeof(infoptr->peers[0]) * infoptr->numpeers);

		totalsize += len;

		/*
		 * move the infoptr to the next entry
		 */
		infoptr = (tracker_info_t *)((char *)infoptr + len);
	}

	/*
	 * malloc space for the predictions
	 */
	if (predictions != NULL) {
		free(predictions);
		predictions_size = 0;
	}

	if ((predictions = (tracker_info_t *)malloc(totalsize)) == NULL) {
		return;
	}

	/*
	 * save the predictions
	 */
	memcpy(predictions, infoptr_first_entry, totalsize);
	predictions_size = totalsize;
}

int
getprediction(uint64_t hash, tracker_info_t **info)
{
	tracker_info_t	*p;
	int		totalsize, size;
	int		retval = 0;

#ifdef	DEBUG
	logmsg("getprediction:hash (0x%016llx)\n", hash);
#endif

	if (predictions == NULL) {
		/*
		 * no predictions, just return
		 */
		return(0);
	}

	p = (tracker_info_t *)predictions;
	totalsize = 0;

	while (totalsize < predictions_size) {
#ifdef	DEBUG
		logmsg("getprediction:pred hash (0x%016llx)\n", p->hash);
#endif
		size = sizeof(tracker_info_t) +
			(sizeof(p->peers[0]) * p->numpeers);

		if (p->hash == hash) {
			/*
			 * found a prediction for this hash
			 */
			if ((*info = (tracker_info_t *)malloc(size)) != NULL) {
				memcpy(*info, p, size);
				retval = 1;
			}

			break;
		}

		totalsize += size;
		p = (tracker_info_t *)((char *)p + size);	
	}

	return(retval);
}

int
trackfile(int sockfd, char *filename, char *range, uint16_t num_trackers,
	in_addr_t *trackers, uint16_t maxpeers, uint16_t num_pkg_servers,
	in_addr_t *pkg_servers, CURL *curlhandle)
{
#ifdef	TIMEIT
	struct timeval		start_time, end_time;
	unsigned long long	s, e;
#endif
	CURLcode	curlcode;
	uint64_t	hash;
	uint16_t	i;
	tracker_info_t	*tracker_info, *infoptr;
	int		info_count;
	char		success;

#ifdef	TIMEIT
	gettimeofday(&start_time, NULL);
#endif

	hash = hashit(filename);

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("trackfile:svc time1: %lld usec file (%s)\n", (e - s), filename);
#endif

#ifdef	DEBUG
{
	int		j;
	struct in_addr	in;

	for (j = 0 ; j < num_trackers ; ++j) {
		in.s_addr = trackers[j];
		logmsg("trackfile:trackers[%d] = (%s)\n", j, inet_ntoa(in));
	}

	for (j = 0 ; j < num_pkg_servers ; ++j) {
		in.s_addr = pkg_servers[j];
		logmsg("trackfile:pkg_servers[%d] = (%s)\n", j, inet_ntoa(in));
	}
}
#endif

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("trackfile:svc time2: %lld usec file (%s)\n", (e - s), filename);
#endif

	/*
	 * see if there is a prediction for this file
	 */
	tracker_info = NULL;
	info_count = getprediction(hash, &tracker_info);

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("trackfile:svc time3: %lld usec file (%s)\n", (e - s), filename);
#endif

#ifdef	DEBUG
	if (info_count == 0) {
		logmsg("trackfile:pred miss (0x%016llx)\n", hash);
	} else {
		logmsg("trackfile:pred hit (0x%016llx)\n", hash);
	}
#endif

	if (info_count == 0) {
		/*
		 * no prediction. need to ask a tracker for peer info for
		 * this file.
		 */
		for (i = 0 ; i < num_trackers; ++i) {
#ifdef	DEBUG
			struct in_addr	in;

			in.s_addr = trackers[i];
			logmsg("trackfile:sending lookup to tracker (%s)\n",
				inet_ntoa(in));
#endif
			info_count = lookup(sockfd, &trackers[i], hash,
				&tracker_info);

			if (info_count > 0) {
				break;
			}

			/*
			 * lookup() mallocs space for 'tracker_info', so need to
			 * free it here since we'll call lookup() again in the
			 * next iteration
			 */
			if (tracker_info != NULL) {
				free(tracker_info);
				tracker_info = NULL;
			}
		}
	}

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("trackfile:svc time4: %lld usec file (%s)\n", (e - s), filename);
#endif

#ifdef	DEBUG
	logmsg("trackfile:info_count (%d)\n", info_count);
#endif

	success = 0;
	infoptr = tracker_info;
	if ((info_count > 0) && (infoptr->hash == hash)) {
		/*
		 * write the prediction info to a file	
		 */
		save_prediction_info(tracker_info, info_count);

#ifdef	TIMEIT
		gettimeofday(&end_time, NULL);
		s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
		e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
		logmsg("trackfile:svc time5: %lld usec file (%s)\n", (e - s),
			filename);
#endif

#ifdef	DEBUG
		logmsg("trackfile:hash (0x%llx) : numpeers (%d)\n",
			infoptr->hash, infoptr->numpeers);

		logmsg("trackfile:peers:\n");

		for (i = 0 ; i < infoptr->numpeers; ++i) {
			struct in_addr	in;

			in.s_addr = infoptr->peers[i].ip;
			logmsg("\t%s : %c %d\n", inet_ntoa(in),
				(infoptr->peers[i].state == DOWNLOADING ?
					'd' : 'r'), infoptr->peers[i].state);
		}
#endif

#ifdef	TIMEIT
		gettimeofday(&end_time, NULL);
		s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
		e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
		logmsg("trackfile:svc time6: %lld usec file (%s)\n", (e - s),
			filename);
#endif

		for (i = 0 ; i < infoptr->numpeers; ++i) {
#ifdef	DEBUG
			{
			struct in_addr	in;
			int		k;

			in.s_addr = infoptr->peers[i].ip;

			if (strncmp(inet_ntoa(in), "10.", 3)) {
				for (k = 0 ; i < num_trackers; ++k) {
					send_msg(sockfd, &trackers[k],
						STOP_SERVER);
				}

				logmsg("trackfile:bogus IP (%s)\n",
					inet_ntoa(in));
				exit(-1);
			}
			}
#endif
			if (getremote(filename, &infoptr->peers[i], range,
					curlhandle) == 0) {
				/*
				 * successful download, exit this loop
				 */
				success = 1;
				break;
			} else {
				/*
				 * mark the peer as 'bad'. we do this by
				 * telling the tracker server to 'unregister'
				 * this hash.
				 */

				tracker_info_t	*info;
				int		len;
				int		j;

				len = sizeof(*info) + sizeof(peer_t);

				if ((info = (tracker_info_t *)malloc(len))
						!= NULL) {

					bzero(info, len);
					info->hash = hash;
					info->numpeers = 1;
					info->peers[0].ip =
						infoptr->peers[i].ip;

					for (j = 0 ; j < num_trackers; ++j) {
						unregister_hash(sockfd,
							&trackers[j], 1, info);
					}

					free(info);
				}
			}
		}
	}

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("trackfile:svc time7: %lld usec file (%s)\n", (e - s), filename);
#endif

	if (!success) {
		/*
		 * unable to download the file from a peer, need to
		 * get it from one of the package servers
		 */

		for (i = 0 ; i < num_pkg_servers ; ++i) {
			peer_t	pkgpeer;

			pkgpeer.ip = pkg_servers[i];
			pkgpeer.state = READY;

			/*
			 * if this is the last package server, then
			 * disable the connection timeout -- this is our
			 * last hope of getting the package.
			 */
			if (i == (num_pkg_servers - 1)) { 
				if ((curlcode = curl_easy_setopt(curlhandle,
					CURLOPT_CONNECTTIMEOUT, 0)) !=
					CURLE_OK) {

					logmsg("getremote:curl_easy_setopt():failed:(%d)\n", curlcode);
				}
			}

			if (getremote(filename, &pkgpeer, range,
					curlhandle) == 0) {
				success = 1;
			}

			/*
			 * reset the connection timeout
			 */
			if (i == (num_pkg_servers - 1)) { 
				if ((curlcode = curl_easy_setopt(curlhandle,
					CURLOPT_CONNECTTIMEOUT, 2)) !=
					CURLE_OK) {

					logmsg("getremote:curl_easy_setopt():failed:(%d)\n", curlcode);
				}
			}

			if (success) {
				break;
			}
		}
	}

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("trackfile:svc time8: %lld usec file (%s)\n", (e - s), filename);
#endif

	if (success) {
		tracker_info_t	info[1];

		bzero(info, sizeof(info));

		info[0].hash = hash;
		info[0].numpeers = 0;

		for (i = 0 ; i < num_trackers; ++i) {
			register_hash(sockfd, &trackers[i], 1, info);
		}
	}

	/*
	 * lookup() and getprediction() mallocs tracker_info
	 */
	if (tracker_info != NULL) {
		free(tracker_info);
	}	

#ifdef	TIMEIT
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("trackfile:svc time: %lld usec file (%s)\n", (e - s), filename);
#endif

	if (success) {
		return(0);
	}

	return(-1);
}

int
doit(int sockfd, uint16_t num_trackers, in_addr_t *trackers, uint16_t maxpeers,
	uint16_t num_pkg_servers, in_addr_t *pkg_servers, CURL *curlhandle)
{
	struct timeval		start_time;
#ifdef	TIMEIT
#endif
	struct timeval		end_time;
	unsigned long long	s, e;
	char			*forminfo;
	char			*range;
	char			filename[PATH_MAX];

	gettimeofday(&start_time, NULL);

	bzero(filename, sizeof(filename));

	if ((forminfo = getenv("QUERY_STRING")) == NULL) {
		senderror(500, "No QUERY_STRING", errno);
		return(0);
	}

	if ((range = getenv("HTTP_RANGE")) != NULL) {
		char	*ptr;

		if ((ptr = strchr(range, '=')) != NULL) {
			range = ptr + 1;
		}
	}

	if (getargs(forminfo, filename) != 0) {
		senderror(500, "getargs():failed", errno);
		return(0);
	}

	/*
	 * the time is 'epoch' time
	 */
	logmsg("%d : doit:file %s\n", start_time.tv_sec, basename(filename));
#ifdef	DEBUG
	logmsg("doit:getting file (%s)\n", filename);
#endif

	/*
	 * if the file is local, just read it off the disk, otherwise, ask
	 * the tracker where the file is
	 */
	if (getlocal(filename, range) != 0) {
		if (trackfile(sockfd, filename, range, num_trackers, trackers,
				maxpeers, num_pkg_servers, pkg_servers,
				curlhandle) != 0) {
			senderror(404, "File not found", 0);
		}
	}

#ifdef	DEBUG
	logmsg("doit:done:file (%s)\n\n", filename);
#endif

#ifdef	TIMEIT
#endif
	gettimeofday(&end_time, NULL);
	s = (start_time.tv_sec * 1000000) + start_time.tv_usec;
	e = (end_time.tv_sec * 1000000) + end_time.tv_usec;
	logmsg("doit:svc time: %lld usec file %s from %s\n\n",
		(e - s) - curltime, basename(filename), fromip);

	return(0);
}

int
main()
{
	CURL		*curlhandle;
	CURLcode	curlcode;
	uint16_t	num_trackers;
	in_addr_t	trackers[MAX_TRACKERS];
	uint16_t	maxpeers;
	uint16_t	num_pkg_servers;
	in_addr_t	pkg_servers[MAX_PKG_SERVERS];
	FILE		*file;
	int		sockfd;
	char		trackers_url[PATH_MAX];
	char		pkg_servers_url[PATH_MAX];
	char		buf[PATH_MAX];

	if ((sockfd = init_tracker_comm(0)) < 0) {
		logmsg("main:init_tracker_comm failed\n");
		return(-1);
	}

	/*
	 * get the IP addresses of the tracker(s) and package server(s)
	 */
	if ((file = fopen("/tmp/stack.conf", "r")) == NULL) {
		fprintf(stderr, "main:fopen\n");
		return(-1);
	}

	fgets(buf, sizeof(buf), file);
	sscanf(buf, "var.trackers = \"%[^\"]", trackers_url);

	fgets(buf, sizeof(buf), file);
	sscanf(buf, "var.pkgservers = \"%[^\"]", pkg_servers_url);

	fclose(file);

	fprintf(stderr, "main:trackers_url (%s)\n", trackers_url);
	fprintf(stderr, "main:pkg_servers_url (%s)\n", pkg_servers_url);
	
	if (init(&num_trackers, trackers_url, trackers, &maxpeers,
			pkg_servers_url, &num_pkg_servers, pkg_servers) != 0) {
		fprintf(stderr, "main:init failed\n");
		return(-1);
	}

	/*
	 * initialize curl
	 */
	if ((curlhandle = curl_easy_init()) == NULL) {
		logmsg("main:curl_easy_init failed\n");
		return(-1);
	}

	if ((curlcode = curl_easy_setopt(curlhandle, CURLOPT_PORT,
			DOWNLOAD_PORT)) != CURLE_OK) {
		logmsg("main:curl_easy_setopt(PORT):failed:(%d)\n",
			curlcode);
		return(-1);
	}

	if ((curlcode = curl_easy_setopt(curlhandle, CURLOPT_HEADERFUNCTION,
			doheaders)) != CURLE_OK) {
		logmsg("main:curl_easy_setopt():failed:(%d)\n", curlcode);
		return(-1);
	}

	if ((curlcode = curl_easy_setopt(curlhandle, CURLOPT_WRITEFUNCTION,
			dobody)) != CURLE_OK) {
		logmsg("main:curl_easy_setopt():failed:(%d)\n", curlcode);
		return(-1);
	}

	/*
	 * set a 2 second timeout in order to connect to the remote web server
	 */
	if ((curlcode = curl_easy_setopt(curlhandle, CURLOPT_CONNECTTIMEOUT,
			2)) != CURLE_OK) {
		logmsg("main:curl_easy_setopt():failed:(%d)\n", curlcode);
		return(-1);
	}

#ifdef	DEBUG
	curl_easy_setopt(curlhandle, CURLOPT_VERBOSE, 1);
#endif

#ifdef	FASTCGI
	while(FCGI_Accept() >= 0) {
#endif
		doit(sockfd, num_trackers, trackers, maxpeers, num_pkg_servers,
			pkg_servers, curlhandle);
#ifdef	FASTCGI
	}
#endif

	return(0);
}

