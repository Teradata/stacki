# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os
import re
import signal
import sys


class Discovery:
    """
    Start or stop a daemon that listens for PXE boots and inserts the new
    nodes into the database.
    """

    _PIDFILE = "/var/run/stack-discovery.pid"
    _LOGFILE = "/var/log/stack-discovery.log"

    _done = False

    async def _monitor_log(self, log_path, process_line):
        # Open our log file
        with open(log_path, 'r') as log:
            # Move to the end
            log.seek(0, 2)

            # Start looking for DHCP requests
            while not self._done:
                line = log.readline()
                
                if line:
                    await process_line(line)
                else:
                    await asyncio.sleep(1)

    async def _process_dhcp_line(self, line):
        match = re.search(r"DHCPDISCOVER from ([0-9a-f:]{17}) via (\S+):", line)
        if match:
            mac_address = match.group(1)
            interface = match.group(2)

            self._logger.info("detected a dhcp request: {} {}".format(mac_address, interface))
        else:
            self._logger.debug("no dhcp match: {}".format(line))

    async def _process_kickstart_line(self, line):
        self._logger.debug("KICKSTART: {}".format(line))

    def _cleanup(self):
        try:
            os.remove(self._PIDFILE)
        except:
            pass

    def _signal_handler(self):
        self._done = True
    
    def _get_pid(self):
        pid = None
        if os.path.exists(self._PIDFILE):
            with open(self._PIDFILE, 'r') as f:
                pid = int(f.read())
        
        return pid
    
    def __init__(self, logging_level=logging.INFO):
        # Set up our logger
        formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")

        try:
            handler = RotatingFileHandler(
                self._LOGFILE,
                maxBytes=10*1024*1024,
                backupCount=3
            )
            handler.setFormatter(formatter)
        except PermissionError:
            # We don't have write access to the logfile, so just blackhole logs
            handler = logging.NullHandler()

        self._logger = logging.getLogger("discovery")
        self._logger.setLevel(logging_level)
        self._logger.addHandler(handler)
    
    def is_running(self):
        "Check if the daemon is running."

        # Is our pidfile there?
        pid = self._get_pid()

        if pid is not None:
            # Is the process still running?
            if os.path.isdir("/proc/{}".format(pid)):
                return True
            else:
                # The process no longer exists, clean up the old files
                self._cleanup()

        return False

    def start(self):
        "Start the node discovery daemon."

        # Only start if there isn't already a daemon running
        if not self.is_running():
            # Fork once to get us into the background
            if os.fork() != 0:
                return
            
            # Seperate ourselves from the parent process
            os.setsid()

            # Fork again so we aren't a session leader
            if os.fork() != 0:
                return

            # Now write out the daemon pid
            with open(self._PIDFILE, 'w') as f:
                f.write("{}".format(os.getpid()))
            
            self._logger.info("discovery daemon started")

            # Get our coroutine event loop
            loop = asyncio.get_event_loop()

            # Setup signal handlers to cleanly stop
            loop.add_signal_handler(signal.SIGINT, self._signal_handler)
            loop.add_signal_handler(signal.SIGTERM, self._signal_handler)

            # Start our event loop
            try:
                loop.run_until_complete(asyncio.gather(
                    self._monitor_log("/var/log/messages", self._process_dhcp_line),
                    self._monitor_log("/var/log/httpd/ssl_access_log", self._process_kickstart_line)
                ))
            finally:
                # All done, clean up
                loop.close()

                self._cleanup()
            
            self._logger.info("discovery daemon stopped")

    def stop(self):
        "Stop the node discovery daemon."

        if self.is_running():
            try:
                os.kill(self._get_pid(), signal.SIGTERM)
            except OSError as e:
                self._logger.exception("unable to stop discovery daemon")
                print("Unable to stop discovery daemon", file=sys.stderr)
        

if __name__ == "__main__":
    discovery = Discovery(logging_level=logging.DEBUG)

    if sys.argv[1] == "--start":
        discovery.start()
    elif sys.argv[1] == "--stop":
        discovery.stop()
    elif sys.argv[1] == "--status":
        if discovery.is_running():
            print("Daemon is running")
        else:
            print("Daemon is stopped")
