/*
 * urlinstall.c - code to set up url (ftp/http) installs
 *
 * Copyright (C) 1997, 1998, 1999, 2000, 2001, 2002, 2003  Red Hat, Inc.
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
 */

#include <newt.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <unistd.h>
#include <errno.h>
#include <glib.h>

#ifdef  STACKI
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <signal.h>
#include <time.h>
#include "../isys/isys.h"
#include "../isys/imount.h"

#include <glib.h>
#include <NetworkManager.h>
#include <nm-client.h>
#endif

#include "../isys/iface.h"

#include "copy.h"
#include "kickstart.h"
#include "loader.h"
#include "loadermisc.h"
#include "lang.h"
#include "log.h"
#include "method.h"
#include "net.h"
#include "method.h"
#include "urlinstall.h"
#include "cdinstall.h"
#include "urls.h"
#include "windows.h"

/* boot flags */
extern uint64_t flags;

char **extraHeaders = NULL;

#ifdef	STACKI
static void writeAvalancheInfo(char *, char *);
static int num_cpus();
static char *get_driver_name(char *);
#ifdef	LATER
static void dump_dhcp4_config(NMDHCP4Config *);
#endif
#endif

#ifdef	STACKI
static char **headers(struct loaderData_s *loaderData)
#else
static char **headers()
#endif
{
    int len = 2;

    /* The list of HTTP headers is unlikely to change, unless a new ethernet
     * device suddenly shows up since last time we downloaded a file.  So,
     * cache the result here to save some time.
     */
    if (extraHeaders != NULL)
        return extraHeaders;

    if ((extraHeaders = realloc(extraHeaders, 2*sizeof(char *))) == NULL) {
        logMessage(CRITICAL, "%s: %d: %m", __func__, __LINE__);
        abort();
    }
    
    checked_asprintf(&extraHeaders[0], "X-Anaconda-Architecture: %s", getProductArch());
    checked_asprintf(&extraHeaders[1], "X-Anaconda-System-Release: %s", getProductName());

    if (FL_KICKSTART_SEND_MAC(flags)) {
        /* find all ethernet devices and make a header entry for each one */
        int i;
        char *dev, *mac;
        struct device **devices;

        devices = getDevices(DEVICE_NETWORK);
        for (i = 0; devices && devices[i]; i++) {
            dev = devices[i]->device;
            mac = iface_mac2str(dev);

#ifdef	STACKI
            char *drivername;

            drivername = get_driver_name(dev);

            logMessage(INFO, "STACKI:headers: mac (%s)", mac);
            logMessage(INFO, "STACKI:headers: drivername (%s)", drivername);
#endif

            if (mac) {
                extraHeaders = realloc(extraHeaders, (len+1)*sizeof(char *));
#ifdef  STACKI
                /* A hint as to our primary interface. */
                if (!strcmp(dev, loaderData->netDev)) {
			checked_asprintf(&extraHeaders[len],
				"X-RHN-Provisioning-MAC-%d: %s %s %s ks",
                                i, dev, mac, drivername);
                } else {
			checked_asprintf(&extraHeaders[len],
				"X-RHN-Provisioning-MAC-%d: %s %s %s",
                                i, dev, mac, drivername);
                }

#else
                checked_asprintf(&extraHeaders[len], "X-RHN-Provisioning-MAC-%d: %s %s",
                                 i, dev, mac);
#endif

                len++;
                free(mac);
            }
#ifdef	STACKI
            if (drivername) {
                free(drivername);
            }
#endif
        }
    }

    if (FL_KICKSTART_SEND_SERIAL(flags) && !access("/sbin/dmidecode", X_OK)) {
        FILE *f;
        char sn[1024];
        char *p;

        if ((f = popen("/sbin/dmidecode -s system-serial-number", "r")) == NULL) {
            logMessage(CRITICAL, "%s: %d: %m", __func__, __LINE__);
            abort();
        }

        /* dmidecode output may be multiline and may include comments, get the
         * first non-comment line.
         */
        while(!feof(f)) {
            p = fgets(sn, sizeof(sn), f);
            if (p == NULL || ferror(f)) {
                logMessage(CRITICAL, "%s: %d: %m", __func__, __LINE__);
                abort();
            }
            if (sn[0] != '#')
                break;
        }
        pclose(f);
        g_strchomp(sn);

        logMessage(INFO, "Extra HTTP Header: X-System-Serial-Number: %s", sn);
        extraHeaders = realloc(extraHeaders, (len+1)*sizeof(char *));
        checked_asprintf(&extraHeaders[len], "X-System-Serial-Number: %s", sn);
        len++;
    }

    extraHeaders = realloc(extraHeaders, (len+1)*sizeof(char *));
    extraHeaders[len] = NULL;
    return extraHeaders;
}

static int loadSingleUrlImage(struct loaderData_s *loaderData, struct iurlinfo *ui,
                              char *dest, char *mntpoint, char *device, int silentErrors) {
    char **ehdrs = NULL;
    int status;

#ifdef	STACKI
    if (!strncmp(ui->url, "http", 4))
        ehdrs = headers(loaderData);
#else
    if (!strncmp(ui->url, "http", 4))
        ehdrs = headers();
#endif

#ifdef	STACKI
	/*
	 * try harder to get the images. since we start lighttpd right before
	 * we call this function, lighttpd may not be ready yet.
	 */
	{
		int	i;

		for (i = 0 ; i < 10 ; ++i) {
			status = urlinstTransfer(loaderData, ui, ehdrs, dest);

			if (status == 0) {
				break;
			}

			usleep(200000);
		}
	}
#else
    status = urlinstTransfer(loaderData, ui, ehdrs, dest);
#endif
    if (status) {
        if (!silentErrors) {
            newtWinMessage(_("Error"), _("OK"),
                           _("Unable to retrieve %s."), ui->url);
        }

        return 2;
    }

    if (dest != NULL) {
        if (mountLoopback(dest, mntpoint, device)) {
            logMessage(ERROR, "Error mounting %s on %s: %m", device, mntpoint);
            return 1;
        }
    }

    return 0;
}

static void copyWarnFn (char *msg) {
   logMessage(WARNING, msg);
}

static void copyErrorFn (char *msg) {
   newtWinMessage(_("Error"), _("OK"), _(msg));
}

static int loadUrlImages(struct loaderData_s *loaderData, struct iurlinfo *ui) {
    char *oldUrl, *path, *dest, *slash;
    int rc;

    oldUrl = strdup(ui->url);
    free(ui->url);

    /* Figure out the path where updates.img and product.img files are
     * kept.  Since ui->url points to a stage2 image file, we just need
     * to trim off the file name and look in the same directory.
     */
    if ((slash = strrchr(oldUrl, '/')) == NULL)
        return 0;

    if ((path = strndup(oldUrl, slash-oldUrl)) == NULL)
        path = oldUrl;

    /* grab the updates.img before install.img so that we minimize our
     * ramdisk usage */
    checked_asprintf(&ui->url, "%s/%s", path, "updates.img");

    if (!loadSingleUrlImage(loaderData, ui, "/tmp/updates-disk.img", "/tmp/update-disk",
                            "/dev/loop7", 1)) {
        copyDirectory("/tmp/update-disk", "/tmp/updates", copyWarnFn,
                      copyErrorFn);
        umountLoopback("/tmp/update-disk", "/dev/loop7");
        unlink("/tmp/updates-disk.img");
        unlink("/tmp/update-disk");
    } else if (!access("/tmp/updates-disk.img", R_OK)) {
        unpackCpioBall("/tmp/updates-disk.img", "/tmp/updates");
        unlink("/tmp/updates-disk.img");
    }

    free(ui->url);

    /* grab the product.img before install.img so that we minimize our
     * ramdisk usage */
    checked_asprintf(&ui->url, "%s/%s", path, "product.img");

    if (!loadSingleUrlImage(loaderData, ui, "/tmp/product-disk.img", "/tmp/product-disk",
                            "/dev/loop7", 1)) {
        copyDirectory("/tmp/product-disk", "/tmp/product", copyWarnFn,
                      copyErrorFn);
        umountLoopback("/tmp/product-disk", "/dev/loop7");
        unlink("/tmp/product-disk.img");
        unlink("/tmp/product-disk");
    }

    free(ui->url);
    ui->url = strdup(oldUrl);

    checked_asprintf(&dest, "/tmp/install.img");

    rc = loadSingleUrlImage(loaderData, ui, dest, "/mnt/runtime", "/dev/loop0", 0);
    free(dest);
    free(oldUrl);

    if (rc) {
        if (rc != 2) 
            newtWinMessage(_("Error"), _("OK"),
                           _("Unable to retrieve the install image."));
        return 1;
    }

    return 0;
}

#ifdef STACKI
void
start_httpd()
{
	/*
	 * the first two NULLs are place holders for the 'nextServer' info
	 */
	char	*args[] = { "/lighttpd/sbin/lighttpd", 
				"-f", "/lighttpd/conf/lighttpd.conf",
				"-D", NULL };
	int	pid;
	int	i;
	struct device	**devices;

	/*
	 * try to mount the CD
	 */
	devices = getDevices(DEVICE_CDROM);
	if (devices) {
		for (i = 0; devices[i]; i++) {
			char	*tmp = NULL;

			if (!devices[i]->device) {
				continue;
			}

			if (strncmp("/dev/", devices[i]->device, 5) != 0) {
				checked_asprintf(&tmp, "/dev/%s",
					devices[i]->device);

				free(devices[i]->device);
				devices[i]->device = tmp;
			}

#ifdef	LATER
			devMakeInode(devices[i]->device, "/tmp/stack-cdrom");
#endif

			logMessage(INFO,
				"start_httpd:trying to mount device %s",
				devices[i]->device);
			if (doPwMount(devices[i]->device, "/mnt/cdrom",
				"iso9660", "ro", NULL)) {

				logMessage(ERROR,
					"start_httpd:doPwMount failed\n");
			} else {
				/*
				 * if there are multiple CD drives, exit this
				 * loop after the first successful mount
				 */ 
				if (symlink(devices[i]->device,
						"/tmp/stack-cdrom") != 0) {
					logMessage(ERROR,
						"start_httpd:symlink failed\n");
				}
				break;
			}
		}
	}

	/*
	 * start the service
	 */
	pid = fork();
	if (pid != 0) {
#ifdef	LATER
		/*
		 * don't close stdin or stdout. this causes problems
		 * with mini_httpd as it uses these file descriptors for
		 * it's CGI processing
		 */
		close(2);
#endif
		execv(args[0], args);
		logMessage(ERROR, "start_httpd:lighttpd failed\n");
	}
}
#endif

char *mountUrlImage(struct installMethod *method, char *location,
                    struct loaderData_s *loaderData) {
    urlInstallData *stage2Data = (urlInstallData *) loaderData->stage2Data;
    struct iurlinfo ui;

    enum { URL_STAGE_MAIN, URL_STAGE_FETCH,
           URL_STAGE_DONE } stage = URL_STAGE_MAIN;

    memset(&ui, 0, sizeof(ui));

    while (stage != URL_STAGE_DONE) {
        switch(stage) {
            case URL_STAGE_MAIN: {
                /* If the stage2= parameter was given (or inferred from repo=)
                 * then use that configuration info to fetch the image.  This
                 * could also have come from kickstart.  Else, we need to show
                 * the UI.
                 */
                if (loaderData->method == METHOD_URL && stage2Data) {
                    urlinfo_copy(&ui, stage2Data);
                    logMessage(INFO, "URL_STAGE_MAIN: url is %s", ui.url);

                    if (!ui.url) {
                        logMessage(ERROR, "missing URL specification");
                        loaderData->method = -1;
                        free(loaderData->stage2Data);
                        loaderData->stage2Data = NULL;

                        if (loaderData->inferredStage2)
                            loaderData->invalidRepoParam = 1;

                        break;
                    }

                    /* ks info was adequate, lets skip to fetching image */
                    stage = URL_STAGE_FETCH;
                    break;
                } else {
                    char *substr;

                    if (urlMainSetupPanel(loaderData, &ui)) {
                        loaderData->stage2Data = NULL;
                        return NULL;
                    }

                    /* If the user-provided URL points at a repo instead of
                     * a stage2 image, fix it up now.
                     */
                    substr = strstr(ui.url, ".img");
                    if (!substr || (substr && *(substr+4) != '\0')) {
                        loaderData->instRepo = strdup(ui.url);

                        checked_asprintf(&ui.url, "%s/images/install.img",
                                         ui.url);
                    }

                    loaderData->invalidRepoParam = 1;
                }

                stage = URL_STAGE_FETCH;
                break;
            }

            case URL_STAGE_FETCH: {
#ifdef  STACKI
                /*
                 * before we start the web server, make sure /tmp/stack.conf
                 * exists
                 */
                if (access("/tmp/stack.conf", F_OK) != 0) {
                    writeAvalancheInfo(NULL, NULL);	
                }
                start_httpd();
#endif
                if (loadUrlImages(loaderData, &ui)) {
                    stage = URL_STAGE_MAIN;

                    if (loaderData->method >= 0)
                        loaderData->method = -1;

                    if (loaderData->inferredStage2)
                        loaderData->invalidRepoParam = 1;
                } else {
                    stage = URL_STAGE_DONE;
                }

                break;
            }

            case URL_STAGE_DONE:
                break;
        }
    }

    return ui.url;
}

#ifdef	STACKI
char *
get_driver_name(char *dev)
{
	FILE	*file;
	int	retval = 1;
	char	field1[80];
	char	device[80];
	char	module[80];

	if ((file = fopen("/tmp/modprobe.conf", "r")) == NULL) {
		return(strdup("none"));
	}

	while (retval != EOF) {
		memset(field1, 0, sizeof(field1));
		memset(device, 0, sizeof(device));
		memset(module, 0, sizeof(module));

		retval = fscanf(file, "%s", field1);
		if ((retval == 1) && (strcmp(field1, "alias") == 0)) {

			retval = fscanf(file, "%s %s", device, module);
			if ((retval == 2) && (strcmp(device, dev) == 0)) {
				fclose(file);
				return(strdup(module));
			}
		}
	}

	fclose(file);
	return(strdup("none"));
}


/*
 * the file /tmp/interfaces will help us on frontend installs when
 * we are associating MAC addresses with IP address and with driver
 * names
 *
 * XXX: this code segment is copy of the code in the function below, so
 * if in future releases of the anaconda installer if the loop in the
 * code segment below changes, then this function will have to be updated
 * too.
 */

void
writeInterfacesFile(struct loaderData_s *loaderData)
{
	struct device	**devices;
	int		i, fd;
	char		*dev, *mac, tmpstr[128], *drivername;

	logMessage(INFO, "STACKI:writeInterfacesFile");

	if ((fd = open("/tmp/interfaces",
			O_WRONLY|O_CREAT|O_TRUNC, 0666)) < 0) {
		logMessage(ERROR, "STACKI:writeInterfacesFile:failed to open '/tmp/interfaces'");
		return;
	}

	devices = getDevices(DEVICE_NETWORK);
	for (i = 0; devices && devices[i]; i++) {
		dev = devices[i]->device;
		mac = iface_mac2str(dev);

		drivername = get_driver_name(dev);

		if (mac) {
                        /* A hint as to our primary interface. */
                        if (!strcmp(dev, loaderData->netDev)) {
                                snprintf(tmpstr, sizeof(tmpstr),
                                "X-RHN-Provisioning-MAC-%d: %s %s %s ks\r\n",
                                i, dev, mac, drivername);
                        } else { 
                                snprintf(tmpstr, sizeof(tmpstr),
                                "X-RHN-Provisioning-MAC-%d: %s %s %s\r\n",
                                i, dev, mac, drivername);
                        } 

			if (write(fd, tmpstr, strlen(tmpstr)) < 0) {
				logMessage(ERROR,
				    "STACKI:writeInterfacesFile::write failed");
			}

			free(mac);
		}

		free(drivername);
	}

	close(fd);
	return;
}
#endif

#ifdef	STACKI
char	*trackers = NULL;
char	*pkgservers = NULL;
#endif

int getFileFromUrl(char * url, char * dest, 
                   struct loaderData_s * loaderData) {
    struct iurlinfo ui;
    char **ehdrs = NULL;
    int rc;
    iface_t iface;
#ifdef  STACKI
    NMClient *client = NULL;
    NMState state;
    const GPtrArray *devices;
    int i;
#endif

    iface_init_iface_t(&iface);

#ifdef  STACKI
    if (kickstartNetworkUp(loaderData, &iface)) {
        logMessage(ERROR, "STACKI:getFileFromUrl:unable to bring up network");
        return(1);
    }

    /*
     * get the 'next-server' value from the dhcp response
     */
    g_type_init();

    if ((client = nm_client_new()) == NULL) {
        logMessage(ERROR, "STACKI:getFileFromUrl:nm_client_new() failed");
        return(1);
    }

    if ((state = nm_client_get_state(client)) != NM_STATE_CONNECTED) {
        logMessage(ERROR, "STACKI:getFileFromUrl:nm_client_get_state() failed");
        logMessage(INFO, "STACKI:getFileFromUrl:g_object_unref:client 0x%lx",
            (unsigned long int)client);
        g_object_unref(client);
        return(1);
    }

    devices = nm_client_get_devices(client);
    for (i = 0; i < devices->len; i++) {
        NMDevice *candidate = g_ptr_array_index(devices, i);
        const char *devname = nm_device_get_iface(candidate);
        NMDHCP4Config *dhcp = NULL;
        const char *server_name = NULL;
        char nextserver[INET_ADDRSTRLEN+1];

        if (nm_device_get_state(candidate) != NM_DEVICE_STATE_ACTIVATED)
            continue;

        if (strcmp(iface.device, devname))
            continue;

        dhcp = nm_device_get_dhcp4_config(candidate);
        if (!dhcp) {
            logMessage(ERROR, "no boot options received by DHCP");
            continue;
        }

        server_name = nm_dhcp4_config_get_one_option(dhcp, "server_name");
        if (server_name) {
        	strcpy(nextserver, server_name);
		loaderData->nextServer = strdup(nextserver);
	} else {
        	loaderData->nextServer = NULL;
	}

        /*
         * If no server_name use the gateway.
         */
        if (!loaderData->nextServer) {
            const char *routers = NULL;
            char gateway[INET_ADDRSTRLEN+1];

            routers = nm_dhcp4_config_get_one_option(dhcp, "routers");
            if (routers) {
                strcpy(gateway, routers);
                loaderData->nextServer = strdup(gateway);
            }
        }
    }

    logMessage(INFO, "STACKI:getFileFromUrl:g_object_unref:2:client 0x%lx",
        (unsigned long int)client);
    g_object_unref(client);

    logMessage(INFO, "%s: nextServer %s",
		"STACKI:getFileFromUrl", loaderData->nextServer);
#else
    if (kickstartNetworkUp(loaderData, &iface)) {
        logMessage(ERROR, "unable to bring up network");
        return 1;
    }
#endif

    memset(&ui, 0, sizeof(ui));

#ifdef	STACKI
{
	int	string_size;
	int	ncpus;
	char	np[16];
	char	*arch;
	char	*base;
	char	*host;
	char	*file;

#if defined(__i386__)
	arch = "i386";
#elif defined(__x86_64__)
	arch = "x86_64";
#endif

	if (!strlen(url)) {
		base = strdup("install/sbin/kickstart.cgi");
		host = strdup(loaderData->nextServer);
	}
	else {
		char	*p, *q;

		base = NULL;
		host = NULL;

		p = strstr(url, "//");
		if (p != NULL) {
			p += 2;

			/*
			 * 'base' is the file name
			 */
			base = strchr(p, '/');
			if (base != NULL) {
				base += 1;
			}

			/*
		 	 * now get the host portion of the URL
			 */
			q = strchr(p, '/');
			if (q != NULL) {
				*q = '\0';
				host = strdup(p);
			}
		}
		
		if (!base || !host) {
			logMessage(ERROR,
				"kickstartFromUrl:url (%s) not well formed.\n",
				url);
			return(1);
		}
	}

	/*
	 * seed random number generator
	 * Used for nack backoff.
	 */
	srand(time(NULL));

	ncpus = num_cpus();
	sprintf(np, "%d", ncpus);

	string_size = strlen("https://") + strlen(host) + strlen("/") +
		strlen(base) + strlen("?arch=") + strlen(arch) +
		strlen("&np=") + strlen(np) + 1;

	if ((file = alloca(string_size)) == NULL) {
		logMessage(ERROR, "kickstartFromUrl:alloca failed\n");
		return(1);
	}
	memset(file, 0, string_size);

	sprintf(file, "https://%s/%s?arch=%s&np=%s", host, base, arch, np);

	logMessage(INFO, "ks location: %s", file);

	ui.url = file;

        if (!strncmp(ui.url, "http", 4)) {
            ehdrs = headers(loaderData);
        }
    }
#else
    ui.url = url;

    logMessage(INFO, "file location: %s", url);

    if (!strncmp(url, "http", 4)) {
        ehdrs = headers();
    }
#endif

#ifdef	STACKI
    {
	int retry = 0;

	while (retry < 60) {
		rc = urlinstTransfer(loaderData, &ui, ehdrs, dest);
		if (rc) {
			logMessage(WARNING, "STACKI:failed to retrieve %s", ui.url);
			++retry;
			sleep(1);
		} else {
			break;
		}
	}
    }
#else
    rc = urlinstTransfer(loaderData, &ui, ehdrs, dest);
#endif

    if (rc) {
        logMessage(ERROR, "failed to retrieve %s", ui.url);
        return 1;
    }

#ifdef	STACKI
    if (trackers == NULL) {
	if (loaderData->nextServer != NULL) {
		trackers = strdup(loaderData->nextServer);
	} else {
		trackers = strdup("127.0.0.1");
	}
    }

    if (pkgservers == NULL) {
	if (loaderData->nextServer != NULL) {
		pkgservers = strdup(loaderData->nextServer);
	} else {
		pkgservers = strdup("127.0.0.1");
	}
    }

    writeAvalancheInfo(trackers, pkgservers);

    free(trackers);
    free(pkgservers);
#endif

    return 0;
}

/* pull kickstart configuration file via http */
int kickstartFromUrl(char * url, struct loaderData_s * loaderData) {
    return getFileFromUrl(url, "/tmp/ks.cfg", loaderData);
}

void setKickstartUrl(struct loaderData_s * loaderData, int argc,
		    char ** argv) {
    char *substr = NULL;
    gchar *url = NULL, *proxy = NULL;
    gboolean noverifyssl = FALSE;
    GOptionContext *optCon = g_option_context_new(NULL);
    GError *optErr = NULL;
    GOptionEntry ksUrlOptions[] = {
        { "url", 0, 0, G_OPTION_ARG_STRING, &url, NULL, NULL },
        { "proxy", 0, 0, G_OPTION_ARG_STRING, &proxy, NULL, NULL },
        { "noverifyssl", 0, 0, G_OPTION_ARG_NONE, &noverifyssl, NULL, NULL },
        { NULL },
    };

    logMessage(INFO, "kickstartFromUrl");

    g_option_context_set_help_enabled(optCon, FALSE);
    g_option_context_add_main_entries(optCon, ksUrlOptions, NULL);

    if (!g_option_context_parse(optCon, &argc, &argv, &optErr)) {
        startNewt();
        newtWinMessage(_("Kickstart Error"), _("OK"),
                       _("Bad argument to URL kickstart method "
                         "command: %s"), optErr->message);
        g_error_free(optErr);
        g_option_context_free(optCon);
        return;
    }

    g_option_context_free(optCon);

    if (!url) {
        newtWinMessage(_("Kickstart Error"), _("OK"),
                       _("Must supply a --url argument to Url kickstart method."));
        return;
    }

    /* determine install type */
    if (strncmp(url, "http", 4) && strncmp(url, "ftp://", 6)) {
        newtWinMessage(_("Kickstart Error"), _("OK"),
                       _("Unknown Url method %s"), url);
        return;
    }

    substr = strstr(url, ".img");
    if (!substr || (substr && *(substr+4) != '\0')) {
        loaderData->instRepo = strdup(url);
        loaderData->instRepo_noverifyssl = noverifyssl;
    } else {
        if ((loaderData->stage2Data = calloc(sizeof(urlInstallData), 1)) == NULL)
            return;

        loaderData->method = METHOD_URL;
        ((urlInstallData *)loaderData->stage2Data)->url = url;
        ((urlInstallData *)loaderData->stage2Data)->noverifyssl = noverifyssl;
    }

    if (proxy) {
        splitProxyParam(proxy, &loaderData->proxyUser,
			       &loaderData->proxyPassword,
			       &loaderData->proxy);
    }
    logMessage(INFO, "results of url ks, url %s", url);
}

#ifdef	STACKI
static int
num_cpus()
{
	FILE	*file;
	int	cpus = 0;
	char	str[128];

	if ((file = fopen("/proc/cpuinfo", "r")) != NULL) {

		while (fscanf(file, "%s", str) != EOF) {
			if (strcmp(str, "processor") == 0) {
				++cpus;
			}
		}

		fclose(file);
	}

	/*
	 * always return at least 1 CPU
	 */
	if (cpus == 0) {
		cpus = 1;
	}

	return(cpus);
}

static void
writeAvalancheInfo(char *trackers, char *pkgservers)
{
	int	fd;
	char	str[512];

	if ((fd = open("/tmp/stack.conf",
					O_WRONLY|O_CREAT|O_TRUNC, 0666)) < 0) {
		logMessage(ERROR, "STACKI:writeAvalancheInfo:failed to open '/tmp/stack.conf'");
	}

	/*
	 * the next server (the ip address of the server that gave us a
	 * kickstart file), is passed to lighttpd through a configuration file.
	 * write that value into it.
	 */
	if (trackers != NULL) {
		sprintf(str, "var.trackers = \"%s\"\n", trackers);
	} else {
		sprintf(str, "var.trackers = \"127.0.0.1\"\n");
	}

	if (write(fd, str, strlen(str)) < 0) {
		logMessage(ERROR, "STACKI:writeAvalancheInfo:write failed");
	}

	if (pkgservers != NULL) {
		sprintf(str, "var.pkgservers = \"%s\"\n", pkgservers);
	} else {
		sprintf(str, "var.pkgservers = \"127.0.0.1\"\n");
	}

	if (write(fd, str, strlen(str)) < 0) {
		logMessage(ERROR, "STACKI:writeAvalancheInfo:write failed");
	}

	close(fd);
}

#ifdef	LATER
/*
 * for debugging NetworkManager DHCP responses
 */
static void
print_one_dhcp4_option (gpointer key, gpointer data, gpointer user_data)
{
	const char *option = (const char *) key;
	const char *value = (const char *) data;

	g_print ("  %s:   %s\n", option, value);
}

static void
dump_dhcp4_config (NMDHCP4Config *config)
{
	GHashTable *options = NULL;

	if (!config) {
		return;
	}

	g_print("STACKI:dump_dhcp4_config:DHCP4 Options:\n");

	g_object_get(G_OBJECT (config), NM_DHCP4_CONFIG_OPTIONS, &options,
		NULL);
        g_hash_table_foreach(options, print_one_dhcp4_option, NULL);
}
#endif

#endif

/* vim:set shiftwidth=4 softtabstop=4: */
