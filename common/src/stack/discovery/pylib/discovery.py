# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import asyncio
import ipaddress
from itertools import filterfalse
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import re
import signal
import socket
import subprocess
import sys
import time

from stack.api.get import GetAttr
from stack.commands import Command
from stack.exception import CommandError
import stack.mq


class Discovery:
    """
    Start or stop a daemon that listens for PXE boots and inserts the new
    nodes into the database.
    """

    _PIDFILE = "/var/run/stack-discovery.pid"
    _LOGFILE = "/var/log/stack-discovery.log"

    _get_next_ip_address_cache = {}
    _get_ipv4_network_for_interface_cache = {}

    @property
    def hostname(self):
        return f"{self._base_name}-{self._rack}-{self._rank}"

    def _get_ipv4_network_for_interface(self, interface):
        """
        Return an IPv4Network object for a given interface, caching the results in the process.
        """

        ipv4_network = self._get_ipv4_network_for_interface_cache.get(interface)
        
        # If we don't have a network in the cache, create it
        if ipv4_network is None:
            results = subprocess.run(
                ["ip", "-o", "-4", "address"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8"
            )            
            for line in results.stdout.splitlines():
                match = re.match(r'\d+:\s+(\S+)\s+inet\s+(\S+)', line)
                if match:
                    if match.group(1) == interface:
                        ipv4_network = ipaddress.IPv4Interface(match.group(2)).network
                        self._get_ipv4_network_for_interface_cache[interface] = ipv4_network

                        self._logger.debug("found network: %s", ipv4_network)
                        break
                else:
                    self._logger.debug("ip regex didn't match line: %s", line)
        
        return ipv4_network        

    def _get_hosts_for_interface(self, interface):
        """
        Get a iterator of IPv4Address objects for this interface, if it exists in the database
        and is pxe bootable. If it isn't a valid interface, return None.
        """

        # Get an IPv4Network for this interface passed in
        ipv4_network = self._get_ipv4_network_for_interface(interface)
        
        if ipv4_network is not None:
            # Figure out the gateway for the interface and check that pxe is true
            self._command.db.clearCache()
            for row in self._command.call("list.network"):
                if (
                    row['address'] == str(ipv4_network.network_address) and 
                    row['mask'] == str(ipv4_network.netmask)
                ):
                    if row['pxe'] == True:
                        # Make sure to filter out the gateway IP address
                        gateway = ipaddress.IPv4Address(row['gateway'])
                        return filterfalse(lambda x: x == gateway, ipv4_network.hosts())
                    else:
                        self._logger.warning("pxe not enabled on interface: %s", interface)
                    break
            else:
                self._logger.warning("unknown network for interface: %s", interface)
        
        # We couldn't find the network or it wasn't pxe enabled
        return None

    def _get_next_ip_address(self, interface):
        """
        Get the next available IP address for the network on the provided interface.
        Return None if we are out of IP addresses or if the interface is not valid.
        """

        # See if we need to get the hosts() iterator for this interface
        if interface not in self._get_next_ip_address_cache:
            # Get the hosts iterator for this interface, return None if it isn't valid
            hosts = self._get_hosts_for_interface(interface)
            if hosts is None:
                return None

            self._get_next_ip_address_cache[interface] = hosts

        # Find the next available IP address
        for ip_address in self._get_next_ip_address_cache[interface]:
            self._logger.debug("trying IP address: %s", ip_address)
            
            # Make sure this IP isn't already taken
            self._command.db.clearCache()
            for row in self._command.call("list.host.interface"):
                if (
                    row['ip'] == str(ip_address) and
                    not row['interface'].startswith("vlan")
                ):
                    self._logger.debug("IP address already taken: %s", ip_address)
                    break
            else:
                # Looks like it is free
                self._logger.debug("IP address is free: %s", ip_address)
                return ip_address
        
        # No IP addresses left
        return None

    def _add_node(self, interface, mac_address, ip_address):
        # Figure out the network for this interface
        network = None
        ipv4_network = self._get_ipv4_network_for_interface(interface)
        if ipv4_network is not None:
            self._command.db.clearCache()
            for row in self._command.call("list.network"):
                if (
                    row['address'] == str(ipv4_network.network_address) and 
                    row['mask'] == str(ipv4_network.netmask)
                ):
                    network = row['network']
                    break
        
        # The network should alway be able to be found, unless something deleted it since the 
        # discovery daemon started running
        if network is not None:
            # Add our new node
            result = subprocess.run([
                "/opt/stack/bin/stack",
                "add",
                "host",
                self.hostname,
                f"appliance={self._appliance_name}",
                f"rack={self._rack}",
                f"rank={self._rank}",
                f"box={self._box}"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
            
            if result.returncode != 0:
                self._logger.error("failed to add host %s:\n%s", self.hostname, result.stderr)
                return

            # Add the node's interface
            result = subprocess.run([
                "/opt/stack/bin/stack",
                "add",
                "host",
                "interface",
                self.hostname,
                "interface=NULL",
                "default=true",
                f"mac={mac_address}",
                f"name={self.hostname}",
                f"ip={ip_address}",
                f"network={network}"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
            
            if result.returncode != 0:
                self._logger.error("failed to add interface for host %s:\n%s", self.hostname, result.stderr)
                return
            
            # Set the new node's install action
            result = subprocess.run([
                "/opt/stack/bin/stack",
                "set",
                "host",
                "installaction",
                self.hostname,
                f"action={self._install_action}"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
            
            if result.returncode != 0:
                self._logger.error("failed to set install action for host %s:\n%s", self.hostname, result.stderr)
                return

            if self._install:
                # Set the new node to install on boot
                result = subprocess.run([
                    "/opt/stack/bin/stack",
                    "set",
                    "host",
                    "boot",
                    self.hostname,
                    "action=install"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
                    
                if result.returncode != 0:
                    self._logger.error("failed to set boot action for host %s:\n%s", self.hostname, result.stderr)
                    return
            else:
                # Set the new node to OS on boot
                result = subprocess.run([
                    "/opt/stack/bin/stack",
                    "set",
                    "host",
                    "boot",
                    self.hostname,
                    "action=os"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
                    
                if result.returncode != 0:
                    self._logger.error("failed to set boot action for host %s:\n%s", self.hostname, result.stderr)
                    return
            
            # Sync the global config
            result = subprocess.run([
                "/opt/stack/bin/stack",
                "sync",
                "config"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
            
            if result.returncode != 0:
                self._logger.error("unable to sync global config:\n%s", result.stderr)
                return

            # Sync the host config
            result = subprocess.run([
                "/opt/stack/bin/stack",
                "sync",
                "host",
                "config",
                self.hostname
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
            
            if result.returncode != 0:
                self._logger.error("unable to sync host config:\n%s", result.stderr)
                return

            self._logger.info("successfully added host %s", self.hostname)

            # Post the host added message
            message = json.dumps({
                'channel': "discovery",
                'message': {
                    'type': "add",
                    'interface': interface,
                    'mac_address': mac_address,
                    'ip_address': str(ip_address),
                    'hostname': self.hostname
                }
            })

            self._socket.sendto(message.encode(), ("localhost", stack.mq.ports.publish))
        else:
            self._logger.error("no network exists for interface %s", interface)

    def _process_dhcp_line(self, line):
        # See if we are a DHCPDISCOVER message
        match = re.search(r"DHCPDISCOVER from ([0-9a-f:]{17}) via (\S+)(:|$)", line)
        if match:
            mac_address = match.group(1)
            interface = match.group(2)

            self._logger.info("detected a dhcp request: %s %s", mac_address, interface)

            # Is this a new MAC address?
            self._command.db.clearCache()
            for row in self._command.call("list.host.interface"):
                if row['mac'] == mac_address:
                    self._logger.debug("node is already known: %s %s", mac_address, interface)
                    break
            else:
                self._logger.info("found a new node: %s %s", mac_address, interface)

                # Make sure we have an IP for it
                ip_address = self._get_next_ip_address(interface)
                if ip_address is None:
                    self._logger.error("no IP addresses available for interface %s", interface)
                else:
                    # Add the new node
                    self._add_node(interface, mac_address, ip_address)

                    # Increment the rank
                    self._rank += 1                    
        else:
            if "DHCPDISCOVER" in line:
                self._logger.warning("DHCPDISCOVER found in line but didn't match regex:\n%s", line)

    def _process_kickstart_line(self, line):
        if re.search("install/sbin(/public)?/profile.cgi", line):
            parts = line.split()
            
            try:
                ip_address = ipaddress.ip_address(parts[0])
                status_code = int(parts[8])
                
                # Post the host kickstart message
                message = json.dumps({
                    'channel': "discovery",
                    'message': {
                        'type': "kickstart",
                        'ip_address': str(ip_address),
                        'status_code': status_code
                    }
                })

                self._socket.sendto(message.encode(), ("localhost", stack.mq.ports.publish))
            except ValueError as e:
                self._logger.error("Invalid Apache log format: %s", line)

    async def _monitor_log(self, log_path, process_line):
        # Open our log file
        with open(log_path, 'r') as log:
            # Move to the end
            log.seek(0, 2)

            # Start looking for new lines in the log file
            while not self._done:
                line = log.readline()
                
                if line:
                    process_line(line)
                else:
                    await asyncio.sleep(1)
    
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
            if os.path.isdir(f"/proc/{pid}"):
                return True
            else:
                # The process no longer exists, clean up the old files
                self._cleanup()

        return False

    def start(self, command, appliance_name=None, base_name=None, 
        rack=None, rank=None, box=None, install_action=None, install=None):    
        """
        Start the node discovery daemon.
        """

        # Only start if there isn't already a daemon running
        if not self.is_running():
            # Make sure our appliance name is valid
            if appliance_name:
                try:
                    command.call("list.appliance", [appliance_name])
                    self._appliance_name = appliance_name
                except CommandError:
                    raise ValueError(f"Unknown appliance with name {appliance_name}")
            else:
                self._appliance_name = "backend"
            
            # Set up the base name
            if base_name:
                self._base_name = base_name
            else:
                self._base_name = self._appliance_name
            
            # Set up the rack
            if rack is None:
                self._rack = int(GetAttr("discovery.base.rack"))
            else:
                self._rack = int(rack)
            
            # Set up the rank
            if rank is None:
                # Start with with default
                self._rank = int(GetAttr("discovery.base.rank"))

                # Try to pull the next rank based on the DB
                for host in command.call("list.host"):
                    if (
                        host['appliance'] == self._appliance_name and 
                        int(host['rack']) == self._rack and
                        int(host['rank']) >= self._rank
                    ):
                        self._rank = int(host['rank']) + 1  
            else:
                self._rank = int(rank)
            
            # Set up box and make sure it is valid
            if box is None:
                self._box = "default"
            else:
                try:
                    command.call("list.box", [box])
                    self._box = box
                except CommandError:
                    raise ValueError(f"Unknown box with name {box}")
            
            # Set up install_action and make sure is is valid
            if install_action is None:
                self._install_action = "default"
            else:
                for action in command.call("list.bootaction"):
                    if action['type'] == "install" and action['bootaction'] == install_action:
                        self._install_action = install_action
                        break
                else:
                    raise ValueError(f"Unknown install action with name {install_action}")
            
            # Set up if we are installing the OS on boot
            if install is None:
                self._install = True
            else:
                self._install = bool(install)

            # Find our apache log
            if os.path.isfile("/var/log/httpd/ssl_access_log"):
                kickstart_log = "/var/log/httpd/ssl_access_log"
            elif os.path.isfile("/var/log/apache2/ssl_access_log"):
                kickstart_log = "/var/log/apache2/ssl_access_log"
            else:
                raise ValueError("Apache log does not exist")
            
            # Fork once to get us into the background
            if os.fork() != 0:
                return
            
            # Close stdin, stdout, stderr of our daemon
            os.close(0)
            os.close(1)
            os.close(2)
            
            # Seperate ourselves from the parent process
            os.setsid()

            # Fork again so we aren't a session leader
            if os.fork() != 0:
                # Directly end this parent process, so it doesn't create another
                # path back up to the caller
                sys.exit(0)
            
            # Reconnect to the db via the command connection passed in, so when
            # the parent process closes theirs, we still have an open socket
            self._command = command
            self._command.db.database.connect()
            self._command.db.link = self._command.db.database.cursor()

            # Open the message queue socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
            status_code = 0
            self._done = False
            try:
                loop.run_until_complete(asyncio.gather(
                    self._monitor_log("/var/log/messages", self._process_dhcp_line),
                    self._monitor_log(kickstart_log, self._process_kickstart_line)
                ))
            except:
                self._logger.exception("event loop threw an exception")
                status_code = 1
            finally:
                # All done, clean up
                loop.close()
                self._command.db.database.close()
                self._socket.close()
                self._cleanup()
            
            self._logger.info("discovery daemon stopped")

            sys.exit(status_code)

    def stop(self):
        "Stop the node discovery daemon."

        if self.is_running():
            try:
                os.kill(self._get_pid(), signal.SIGTERM)
            except OSError:
                self._logger.exception("unable to stop discovery daemon")
                return False
        
        return True
