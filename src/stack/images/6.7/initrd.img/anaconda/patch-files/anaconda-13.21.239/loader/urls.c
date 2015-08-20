/*
 * urls.c - url handling code
 *
 * Copyright (C) 1997, 1998, 1999, 2000, 2001, 2002, 2009  Red Hat, Inc.
 * All rights reserved.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Author(s): Erik Troan <ewt@redhat.com>
 *            Matt Wilson <msw@redhat.com>
 *            Michael Fulbright <msf@redhat.com>
 *            Jeremy Katz <katzj@redhat.com>
 *            Chris Lumens <clumens@redhat.com>
 */

#include <arpa/inet.h>
#include <ctype.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <newt.h>
#include <regex.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>
#include <netdb.h>
#include <errno.h>
#include <curl/curl.h>

#include "lang.h"
#include "loader.h"
#include "loadermisc.h"
#include "urls.h"
#include "log.h"
#include "windows.h"
#include "net.h"

#define NMATCH 10

/* boot flags */
extern uint64_t flags;

/* This is just a wrapper around the windows.c progress callback that accepts
 * the arguments libcurl provides.
 */
int progress_cb(void *data, double dltotal, double dlnow, double ultotal, double ulnow) {
    struct progressCBdata *cb_data = (struct progressCBdata *) data;

    progressCallback(cb_data, dlnow, dltotal);
    return 0;
}

void urlinfo_copy(struct iurlinfo *dst, const struct iurlinfo *src) {
    dst->url = strdup(src->url);
    dst->noverifyssl = src->noverifyssl;
}

int splitProxyParam(char *param, char **user, char **password, char **proxy) {
    /* proxy=[protocol://][username[:password]@]host[:port] */
    char *pattern = "([A-Za-z]+://)?(([A-Za-z0-9]+)(:[^:@]+)?@)?([^:/]+)(:[0-9]+)?(/.*)?";
    regex_t re;
    regmatch_t pmatch[NMATCH];

    if (regcomp(&re, pattern, REG_EXTENDED)) {
        return 0;
    }

    if (regexec(&re, param, NMATCH, pmatch, 0) == REG_NOMATCH) {
        regfree(&re);
        return 0;
    }

    /* Match 0 is always the whole string (assuming regexec matched anything)
     * so skip it.  Then, these indices are just the number of the starting
     * paren in pattern above.  Make sure to change these whenever changing
     * the pattern.
     */
    if (pmatch[3].rm_so != -1)
        *user = strndup(param+pmatch[3].rm_so, pmatch[3].rm_eo-pmatch[3].rm_so);

    /* Skip the leading colon. */
    if (pmatch[4].rm_so != -1)
        *password = strndup(param+pmatch[4].rm_so+1, pmatch[4].rm_eo-pmatch[4].rm_so-1);

    if (pmatch[5].rm_so != -1) {
        char *portStr = "";

        if (pmatch[6].rm_so != -1)
            portStr = strndup(param+pmatch[6].rm_so, pmatch[6].rm_eo-pmatch[6].rm_so);

        /* If no parameter was given, default to HTTP.  yum will want to know
         * the protocol, and curl will just ignore it if given.
         */
        if (pmatch[1].rm_so != -1) {
            checked_asprintf(proxy, "%.*s%.*s%s", pmatch[1].rm_eo-pmatch[1].rm_so,
                                                  param+pmatch[1].rm_so,
                                                  pmatch[5].rm_eo-pmatch[5].rm_so,
                                                  param+pmatch[5].rm_so,
                                                  portStr);
        } else {
            checked_asprintf(proxy, "http://%.*s%s", pmatch[5].rm_eo-pmatch[5].rm_so,
                                                     param+pmatch[5].rm_so,
                                                     portStr);
        }
    }

    regfree(&re);
    return 1;
}

#ifdef	STACKI
extern char	*trackers;
extern char	*pkgservers;
static int	sleeptime = 0;

static size_t
returnedheaders(void *ptr, size_t size, size_t nmemb, void *userdata)
{
	char	*p, *q;

	if ((p = strchr(ptr, ' ')) != NULL) {
		*p = '\0';
		++p;

		/*
		 * strip whitespace off the back of the string
		 */
		q = p + strlen(p) - 1;
		while (isspace(*q)) {
			if (q <= p) {
				break;
			}
			*q = '\0';
			--q;
		}
		
		if (strcmp(ptr, "X-Avalanche-Trackers:") == 0) {
			trackers = strdup(p);
		} else if (strcmp(ptr, "X-Avalanche-Pkg-Servers:") == 0) {
			pkgservers = strdup(p);
		} else if (strcmp(ptr, "Retry-After:") == 0) {
			sleeptime = atoi(p);
		}
	}

	return(size*nmemb);
}

#define KS_RETRY_MAX 30
#define KS_RETRY_MIN 5

extern void	watchdog_on(short int);
extern void	watchdog_off();

void
serverBusy(short int is_server)
{
	int	sleepmin = KS_RETRY_MIN;

	/*
	 * Don't let the watchdog fire if the kickstart server is
	 * reporting busy
	 */
	watchdog_off();

	if (sleeptime <= 0) {
		/*
		 * Backoff a random interval between KS_RETRY_MIN and
		 * KS_RETRY_MAX
		 */
		sleeptime = sleepmin + ((KS_RETRY_MAX - sleepmin) *
			(rand()/(float)RAND_MAX));
	}

	winStatus(44, 3, _("Server Busy"),
		_("Retry for a kickstart file in %d seconds"), sleeptime, 0);

	/*
	 * this must be in a loop, as the alarm associated with the watchdog
	 * timer is sending a signal which interrupts the sleep().
	 */
	while ((sleeptime = sleep(sleeptime)) != 0) {
		;
	}

	newtPopWindow();

	/*
	 * Re-enable the watchdog
	 */
	watchdog_on(is_server);
}

#endif

int urlinstTransfer(struct loaderData_s *loaderData, struct iurlinfo *ui,
                    char **extraHeaders, char *dest) {
    struct progressCBdata *cb_data;
    CURL *curl = NULL;
    CURLcode status;
    struct curl_slist *headers = NULL;
    char *version;
    FILE *f = NULL;

    logMessage(INFO, "transferring %s", ui->url);

    f = fopen(dest, "w");

    /* Initialize libcurl */
    curl_global_init(CURL_GLOBAL_SSL);
    curl = curl_easy_init();

    checked_asprintf(&version, "anaconda/%s", VERSION);

    curl_easy_setopt(curl, CURLOPT_USERAGENT, version);
    curl_easy_setopt(curl, CURLOPT_URL, ui->url);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, f);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1);
    curl_easy_setopt(curl, CURLOPT_MAXREDIRS, 10);
    curl_easy_setopt(curl, CURLOPT_FAILONERROR, 1);

#ifdef STACKI
    /*
     * make sure the request comes from a privileged port.
     * we'll start at port 1 and then allow a scan up to port 1023
     */
    curl_easy_setopt(curl, CURLOPT_LOCALPORT, 1);
    curl_easy_setopt(curl, CURLOPT_LOCALPORTRANGE, 1023);
#endif

    /* If a proxy was provided, add the options for that now. */
    if (loaderData->proxy && strcmp(loaderData->proxy, "")) {
        curl_easy_setopt(curl, CURLOPT_PROXY, loaderData->proxy);

        if (loaderData->proxyUser && strcmp(loaderData->proxyUser, ""))
            curl_easy_setopt(curl, CURLOPT_PROXYUSERNAME,
                             loaderData->proxyUser);

        if (loaderData->proxyPassword && strcmp(loaderData->proxyPassword, ""))
            curl_easy_setopt(curl, CURLOPT_PROXYPASSWORD,
                             loaderData->proxyPassword);
    }

    if (extraHeaders) {
        int i;
        for (i = 0; extraHeaders[i] != NULL; i++) {
            headers = curl_slist_append(headers, extraHeaders[i]);
        }

        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    }

    if (ui->noverifyssl || FL_NOVERIFYSSL(flags)) {
        curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0);
    }

    /* Only set up the progress bar if we've got a UI to display it. */
    if (FL_CMDLINE(flags)) {
        printf("%s %s...\n", _("Retrieving"), ui->url);
    } else {
        char *filename;

        filename = strrchr(ui->url, '/');
        if (!filename)
           filename = ui->url;

        cb_data = winProgressBar(70, 5, _("Retrieving"), "%s %s...", _("Retrieving"), filename);

        curl_easy_setopt(curl, CURLOPT_NOPROGRESS, 0);
        curl_easy_setopt(curl, CURLOPT_PROGRESSFUNCTION, progress_cb);
        curl_easy_setopt(curl, CURLOPT_PROGRESSDATA, cb_data);
    }

#ifdef	STACKI
    if (strncmp(ui->url, "https", 5) == 0) {
        /*
         * don't verify the authenticity of the peer's certificate
         */
        curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0);

        /*
         * don't verify that the server cert is for the server it is known as
         */
        curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, 0);

        /*
         * only parse the returned headers when we are trying to get a
         * kickstart file (that is, we're using https).
         */
        curl_easy_setopt(curl, CURLOPT_HEADERFUNCTION, returnedheaders);
    }
#endif

    /* Finally, do the transfer. */
    status = curl_easy_perform(curl);

#ifdef	STACKI
{
	/*
	* retry if the server told us it is busy
	*/
	int	done = 0;
	int	tries = 0;

	while (!done && status && (tries < 50)) {
		long	errorcode;

		if (curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE,
				&errorcode) != CURLE_OK) {
			done = 1;
			continue;
		}

		logMessage(INFO, "STACKI: HTTP status code (%ld)", errorcode);

		if (errorcode == 503) {
			serverBusy(loaderData->server);

			logMessage(INFO, "transferring %s", ui->url);
			status = curl_easy_perform(curl);
			++tries;
		} else {
			done = 1;
			continue;
		}
	}
}
#endif
    if (status)
        logMessage(ERROR, "Error downloading %s: %s", ui->url, curl_easy_strerror(status));

    if (!FL_CMDLINE(flags))
       newtPopWindow();

    if (headers)
        curl_slist_free_all(headers);

    fclose(f);
    free(version);

    curl_easy_cleanup(curl);
    curl_global_cleanup();

    return status;
}

char * addrToIp(char * hostname) {
    struct in_addr ad;
    struct in6_addr ad6;
    char *ret;
    struct hostent *host;

    if ((ret = malloc(INET6_ADDRSTRLEN+1)) == NULL)
        return hostname;

    if (inet_ntop(AF_INET, &ad, ret, INET_ADDRSTRLEN) != NULL)
        return ret;
    else if (inet_ntop(AF_INET6, &ad6, ret, INET6_ADDRSTRLEN) != NULL)
        return ret;
    else if ((host = gethostbyname(hostname)) != NULL)
        return host->h_name;
    else
        return NULL;
}

static void setProxySensitivity(newtComponent co, void *dptr) {
    int i;

    /* It's 3 because there are three entry boxes in the proxy grid.  Lame. */
    for (i = 0; i < 3; i++) {
        newtEntrySetFlags(*((newtComponent *) dptr), NEWT_FLAG_DISABLED,
                          NEWT_FLAGS_TOGGLE);
        dptr += sizeof(newtComponent);
    }

    return;
}

int urlMainSetupPanel(struct loaderData_s *loaderData, struct iurlinfo * ui) {
    newtComponent form, okay, cancel, urlEntry, proxyCheckbox;
    newtComponent proxyEntries[3];
    newtComponent answer, text;
    char enableProxy;
    char *url = "", *proxy = "", *proxyUser = "", *proxyPassword = "";
    char * reflowedText = NULL;
    int width, height;
    newtGrid buttons, grid, proxyGrid;
    char * buf = NULL;

    /* Populate the UI with whatever initial value we've got. */
    if (ui && ui->url)
        url = ui->url;

    if (loaderData->proxy)
        proxy = loaderData->proxy;

    if (loaderData->proxyUser)
        proxyUser = loaderData->proxyUser;

    if (loaderData->proxyPassword)
        proxyPassword = loaderData->proxyPassword;

    buttons = newtButtonBar(_("OK"), &okay, _("Back"), &cancel, NULL);

    checked_asprintf(&buf,
                     _("Please enter the URL containing the %s installation image on your server."),
                     getProductName());

    reflowedText = newtReflowText(buf, 47, 5, 5, &width, &height);
    free(buf);

    text = newtTextbox(-1, -1, width, height, NEWT_TEXTBOX_WRAP);
    newtTextboxSetText(text, reflowedText);
    free(reflowedText);

    urlEntry = newtEntry(22, 8, url, 60, (const char **) &url,
                         NEWT_ENTRY_SCROLL);

    /* If we've been provided with proxy settings already, enable the proxy
     * grid.  This will make sure all the fields get filled in, too.
     */
    enableProxy = loaderData->proxy != NULL && strcmp("", loaderData->proxy) ? '*' : ' ';

    proxyCheckbox = newtCheckbox(-1, -1, _("Enable HTTP proxy"), enableProxy,
                                 NULL, &enableProxy);
    newtComponentAddCallback(proxyCheckbox, setProxySensitivity, &proxyEntries);

    proxyEntries[0] = newtEntry(-1, -1, proxy, 35, (const char **) &proxy, NEWT_FLAG_SCROLL);
    proxyEntries[1] = newtEntry(-1, -1, proxyUser, 15, (const char **) &proxyUser, NEWT_FLAG_SCROLL);
    proxyEntries[2] = newtEntry(-1, -1, proxyPassword, 15, (const char **) &proxyPassword, NEWT_FLAG_SCROLL|NEWT_FLAG_PASSWORD);

    /* Set the initial proxy grid sensitivity to match. */
    if (enableProxy == ' ')
        setProxySensitivity(proxyCheckbox, proxyEntries);

    proxyGrid = newtCreateGrid(2, 3);
    newtGridSetField(proxyGrid, 0, 0, NEWT_GRID_COMPONENT,
                     newtLabel(-1, -1, _("Proxy URL")),
                     0, 0, 0, 0, 0, NEWT_ANCHOR_LEFT);
    newtGridSetField(proxyGrid, 1, 0, NEWT_GRID_COMPONENT, proxyEntries[0],
                     0, 0, 0, 0, 0, NEWT_ANCHOR_LEFT);
    newtGridSetField(proxyGrid, 0, 1, NEWT_GRID_COMPONENT,
                     newtLabel(-1, -1, _("Username")),
                     0, 0, 0, 1, 0, NEWT_ANCHOR_LEFT);
    newtGridSetField(proxyGrid, 1, 1, NEWT_GRID_COMPONENT, proxyEntries[1],
                     0, 0, 0, 1, 0, NEWT_ANCHOR_LEFT);
    newtGridSetField(proxyGrid, 0, 2, NEWT_GRID_COMPONENT,
                     newtLabel(-1, -1, _("Password")),
                     0, 0, 0, 1, 0, NEWT_ANCHOR_LEFT);
    newtGridSetField(proxyGrid, 1, 2, NEWT_GRID_COMPONENT, proxyEntries[2],
                     0, 0, 0, 1, 0, NEWT_ANCHOR_LEFT);

    grid = newtCreateGrid(1, 5);
    newtGridSetField(grid, 0, 0, NEWT_GRID_COMPONENT, text,
                     0, 0, 0, 1, 0, 0);
    newtGridSetField(grid, 0, 1, NEWT_GRID_COMPONENT, urlEntry,
                     0, 0, 0, 1, 0, 0);
    newtGridSetField(grid, 0, 2, NEWT_GRID_COMPONENT, proxyCheckbox,
                     0, 0, 0, 1, 0, NEWT_ANCHOR_LEFT);
    newtGridSetField(grid, 0, 3, NEWT_GRID_SUBGRID, proxyGrid,
                     0, 0, 0, 0, 0, NEWT_GRID_FLAG_GROWX);
    newtGridSetField(grid, 0, 4, NEWT_GRID_SUBGRID, buttons,
                     0, 0, 0, 0, 0, NEWT_GRID_FLAG_GROWX);

    form = newtForm(NULL, NULL, 0);
    newtGridAddComponentsToForm(grid, form, 1); 
    newtGridWrappedWindow(grid, _("URL Setup"));
    newtGridFree(grid, 1);

    do {
        answer = newtRunForm(form);
        if (answer != cancel) {
            if (!strlen(url)) {
                newtWinMessage(_("Error"), _("OK"),
                               _("You must enter a URL."));
                continue;
            }

            if (strncmp(url, "http", 4) && strncmp(url, "ftp://", 6)) {
                newtWinMessage(_("Error"), _("OK"),
                               _("URL must be either an ftp or http URL"));
                continue;
            }

            ui->url = strdup(url);

            if (enableProxy == '*') {
               if (strncmp(proxy, "http", 4) && strncmp(proxy, "ftp://", 6)) {
                   newtWinMessage(_("Error"), _("OK"),
                                  _("Proxy must be either an ftp or http URL"));
                   continue;
               }

               loaderData->proxy = strdup(proxy);
               loaderData->proxyUser = strdup(proxyUser);
               loaderData->proxyPassword = strdup(proxyPassword);
            } else {
               loaderData->proxy = "";
               loaderData->proxyUser = "";
               loaderData->proxyPassword = "";
            }

            /* FIXME:  add back in hostname checking */
        }

        break;
    } while (1);

    if (answer == cancel) {
        newtFormDestroy(form);
        newtPopWindow();

        return LOADER_BACK;
    }

    newtFormDestroy(form);
    newtPopWindow();

    return 0;
}
