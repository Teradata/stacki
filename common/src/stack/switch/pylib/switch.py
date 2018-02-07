# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import re
import subprocess
import tempfile
import time
import fcntl
import pexpect
import errno
from ipaddress import IPv4Interface, ip_network
import logging
from logging.handlers import RotatingFileHandler
from stack.commands import Command
import asyncio
import signal
import sys

class Switch():
	def __init__(self, switch_ip_address, switchname='switch', username='admin', password='admin'):
		# Grab the user supplied info, in case there is a difference (PATCH)
		self.switch_ip_address = switch_ip_address
		self.username = username
		self.password = password

		self.stacki_server_ip = None
		self.path = '/tftpboot/pxelinux'
		self.switchname = switchname
		self.check_filename = "%s/%s_check" % (self.path, self.switchname)
		self.download_filename = "%s/%s_running_config" % (self.path, self.switchname)
		self.upload_filename = "%s/%s_upload" % (self.path, self.switchname)

	def __enter__(self):
		# Entry point of the context manager
		return self

	def __exit__(self, *args):
		try:
			self.disconnect()
		except AttributeError:
			## TODO: release file lock here
			print("%s's self.child already terminated or never started." % self.switch_ip_address)


class SwitchDellX1052(Switch):
	"""Class for interfacing with a Dell x1052 switch.
	"""

	def connect(self):
		"""Connect to the switch"""
		try:
			self.child = pexpect.spawn('ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -tt ' +
									   self.switch_ip_address)
			self._expect('User Name:', 10)
			self.child.sendline(self.username)
			self._expect('Password:')
			self.child.sendline(self.password)
		except:
			print("Couldn't connect to the switch")

	def disconnect(self):
		# q will exit out of an existing scrollable more/less type of prompt
		# Probably not necessary, but a bit safer
		self.child.sendline("\nq\n")
		# exit should cleanly exit the ssh
		self.child.sendline("\nexit\n")
		# Just give it a few seconds to exit gracefully before terminate.
		time.sleep(3)
		self.child.terminate()
		

	def _expect(self, look_for, custom_timeout=15):
		try:
			self.child.expect(look_for, timeout=custom_timeout)
		except pexpect.exceptions.TIMEOUT:
			# print "Giving SSH time to close gracefully...",
			for _ in range(9, -1, -1):
				if not self.child.isalive():
					break
				time.sleep(1)
			debug_info = str(str(self.child.before) + str(self.child.buffer) + str(self.child.after))
			self.__exit__()
			raise Exception(self.switch_ip_address + " expected output '" + look_for +
							"' from SSH connection timed out after " +
							str(custom_timeout) + " seconds.\nBuffer: " + debug_info)
		except pexpect.exceptions.EOF:
			self.__exit__()
			raise Exception("SSH connection to " + self.switch_ip_address + " not available.")

	def get_mac_address_table(self):
		"""Download the mac address table"""
		time.sleep(1)
		command = 'show mac address-table'
		self.child.expect('console#', timeout=60)
		with open('/tmp/%s_mac_address_table' % self.switchname, 'wb') as macout:
			self.child.logfile = macout
			self.child.sendline(command)
			time.sleep(1)
			self.send_spacebar(4)
			self.child.expect('console#', timeout=60)
		self.child.logfile = None
	
	def parse_mac_address_table(self):
		"""Parse the mac address table and return list of connected macs"""
		_hosts = []
		with open('/tmp/%s_mac_address_table' % self.switchname, 'r') as f:
			for line in f.readlines():
				if 'dynamic' in line:
					# appends line to list
					# map just splits out the port 
					#   from the interface
					_hosts.append(list(
					  map(lambda x: x.split('/')[-1],
					  line.split())
					))

		return sorted(_hosts, key=lambda x: x[2])

	def get_interface_status_table(self):
		"""Download the interface status table"""
		time.sleep(1)
		command = 'show interface status'
		self.child.expect('console#', timeout=60)
		with open('/tmp/%s_interface_status_table' % self.switchname, 'wb') as macout:
			self.child.logfile = macout
			self.child.sendline(command)
			time.sleep(1)
			self.send_spacebar(4)
			self.child.expect('console#', timeout=60)
		self.child.logfile = None
	
	def parse_interface_status_table(self):
		"""Parse the interface status and return list of port information"""
		_hosts = []
		with open('/tmp/%s_interface_status_table' % self.switchname, 'r') as f:
			for line in f.readlines():
				if 'gi1/0/' in line:
					# appends line to list
					# map just splits out the port 
					#   from the interface
					_hosts.append(list(
					  map(lambda x: x.split('/')[-1],
					  line.split())
					))

		return _hosts


	def get_vlan_table(self):
		"""Download the vlan table"""
		time.sleep(1)
		command = 'show vlan'
		self.child.expect('console#', timeout=60)
		with open('/tmp/%s_vlan_table' % self.switchname, 'wb') as macout:
			print("opening vlan table file")
			self.child.logfile = macout
			self.child.sendline(command)
			time.sleep(1)
			self.send_spacebar(4)
			self.child.expect('console#', timeout=60)
		self.child.logfile = None

	def send_spacebar(self, times=1):
		"""Send Spacebar; Used to read more of the output"""
		command = "\x20"
		for i in range(times):
			self.child.send(command)
			time.sleep(1)

	def download(self, check=False):  # , source, destination):
		"""Download the running-config from the switch to the server"""
		time.sleep(1)
		if not check:
			_output_file = open(self.download_filename, 'w')
		else:
			_output_file = open(self.check_filename, 'w')
		os.chmod(_output_file.name, 0o777)
		_output_file.close()

		download_config = "copy running-config tftp://%s/%s" % (
			self.stacki_server_ip, 
			_output_file.name.split("/")[-1]
			)

		self.child.expect('console#', timeout=60)
		self.child.sendline(download_config)
		self._expect('The copy operation was completed successfully')

	def upload(self):
		"""Upload the file from the switch to the server"""

		upload_name = self.upload_filename.split("/")[-1]
		upload_config = "copy tftp://%s/%s temp" % (
				self.stacki_server_ip, 
				upload_name
				)
		apply_config = "copy temp running-config"
		self.child.expect('console#', timeout=60)
		self.child.sendline(upload_config)
		# Not going to look for "Overwrite file" prompt as it doesn't always show up.
		# self.child.expect('Overwrite file .temp.*\?')
		time.sleep(2)
		self.child.sendline('Y')  # A quick Y will fix the overwrite prompt if it exists.
		self._expect('The copy operation was completed successfully')
		self.child.sendline(apply_config)
		self._expect('The copy operation was completed successfully')

		self.download(True)
		# for debugging the temp files created:
		copied_file = open(self.check_filename).read()
		with open("/tftpboot/checker_file", "w") as f:
			f.write(copied_file)

		copied_file = open(self.upload_filename).read()
		with open("/tftpboot/upload_file", "w") as f:
			f.write(copied_file)


	def apply_configuration(self):
		"""Apply running-config to startup-config"""
		try:
			self.child.expect('console#')
			self.child.sendline('copy running-config startup-config')
			self.child.expect('Overwrite file .startup-config.*\?')
			self.child.sendline('Y')
			self._expect('The copy operation was completed successfully')
		except:
			raise Exception('Could not confirm configuration')
		
	def _vlan_parser(self, vlan_string):
		"""Takes input of a bunch of numbers in gives back a string containing all numbers once.
		The format for all_vlans is expected to be 3-7,9-10,44,3
		Which would be broken into a list like so: 3,4,5,6,7,9,10,44
		This if for inputing to the interface for the general port's vlan settings
		It could also be used to QA the vlans set afterwards. Which is not currently a feature."""
		clean_vlans = set()
		for each_vlan_str in vlan_string.split(","):
			if "-" in each_vlan_str:
				start, end = each_vlan_str.split("-")
				for each_number in range(int(start), int(end) + 1):
					clean_vlans.add(int(each_number))
			else:
				if each_vlan_str:
					clean_vlans.add(int(each_vlan_str))

		all_vlans = ','.join([str(vlan) for vlan in sorted(clean_vlans)])

		return all_vlans

	def get_port_from_interface(self, line):
		""" Get Port from gigabitethernet interface
		interface gigabitethernet1/0/20 returns 20
		"""
		port = line.split('/')[-1]
		return port

	def parse_config(self, config_filename):
		"""Parse the given configuration file and return a list of lists describing the vlan assignments per port."""
		my_list = []
		with open(config_filename) as filename:
			lines = filename.readlines()
		for line in lines:
			if "gigabitethernet" not in line and not parse_port:
				pass
			elif "interface gigabitethernet" in line:
				parse_port = int(line.strip().split("/")[-1:][0])
			elif "interface tengigabitethernet" in line:
				parse_port = int(line.strip().split("/")[-1:][0]) + 48
			elif "!" in line:
				parse_port = None
			elif parse_port:
				parse_vlan = None
				parse_mode = None
				parse_tagged = None
				current_port_properties = [parse_port, parse_mode, parse_vlan, parse_tagged]
				if "switchport" in line:
					current_port_properties = self._parse_switchport(current_port_properties, line)
				my_list[parse_port - 1] = current_port_properties
		return my_list

	def configure(self, persistent=False):
		"""Go through the steps to configure a switch with the config stored in the database."""
		try:
			self.connect()
			self.upload()
			if persistent:
				self.apply_configuration()
		except Exception as found_error:
			print("%s: had exception: %s" % (self.switch_ip_address, str(found_error)))
			self.__exit__()

	def set_filenames(self, filename):
		"""
		Sets filenames for download, upload, and check files in /tftpboot/pxelinux
		"""
		self.switchname = filename
		self.download_filename = "%s/%s_running_config" % (self.path, self.switchname)
		self.upload_filename = "%s/%s_upload" % (self.path, self.switchname)
		self.check_filename = "%s/%s_check" % (self.path, self.switchname)


	def set_tftp_ip(self, ip):
		self.stacki_server_ip = ip

class Discover:
	"""
	Start or stop a daemon that listens to the mac address table and inserts 
	the association into the database
	"""
	def __init__(self, switchname='testing-switch', switch_address=None, frontend_tftp_address=None, logging_level=logging.INFO):
		# Set up our logger
		formatter = logging.Formatter("%(asctime)s $(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S:")
		self._PIDFILE = f"/var/run/{switchname}-switch-discovery.pid" 
		self._LOGFILE = f"/var/log/{switchname}-switch-discovery.log" 
		
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

		self._logger = logging.getLogger(f"{switchname}")
		self._logger.setLevel(logging_level)
		self._logger.addHandler(handler)
		self.switchname = switchname
		self.frontend_tftp_address = frontend_tftp_address
		self.switch_address = switch_address
		self._done = False

	async def _start_switch_connection(self):
		with SwitchDellX1052(self.switch_address, self.switchname) as switch:
			switch.set_tftp_ip(self.frontend_tftp_address)
			while not self._done:
				switch.connect()
				self._logger.info("Show mac address table")
				switch.get_mac_address_table()
				hosts = switch.parse_mac_address_table()
				for vlan, mac, port, _ in hosts:
					self.add_host_to_switch_db(
					vlan,
					mac,
					port
					)

				switch.disconnect()
				await asyncio.sleep(10)
		

	def start(self,command):
		if os.fork() != 0:
			return

		os.close(0)
		os.close(1)
		os.close(2)

		os.setsid()

		if os.fork() != 0:
			sys.exit(0)

		self._command = command
		self._command.db.database.connect()
		self._command.db.link = self._command.db.database.cursor()

		with open(self._PIDFILE, 'w') as f:
			f.write(f'{os.getpid()}')

		self._logger.info(f'{self.switchname} logging started')

		# Get our coroutine event loop
		loop = asyncio.get_event_loop()

		# Setup signal handlers to cleanly stop
		loop.add_signal_handler(signal.SIGINT, self._signal_handler)
		loop.add_signal_handler(signal.SIGTERM, self._signal_handler)
		try:
			loop.run_until_complete(asyncio.gather(
				self._start_switch_connection()
			))
		except:
			self._logger.exception("event loop threw an exception")
			status_code = 1
		finally:
			# All done, clean up
			loop.close()
			self._command.db.database.close()
			#self._cleanup()

		self._logger.info("Switch discovery stopped")

	def stop(self):
		self.keep_running = False
		# Make sure not to kill the process while connected to the switch
		try:
			os.kill(self._get_pid(), signal.SIGTERM)
		except OSError:
			self._logger.exception("unable to stop switch discovery")
			return False

		return True

	def _signal_handler(self):
		self._done = True

	def _get_pid(self):
		pid = None
		if os.path.exists(self._PIDFILE):
			with open(self._PIDFILE) as f:
				pid = int(f.read())
		return pid

	def is_running(self):
		"Check if the daemon is running"

		# Is our pidfile there
		pid = self._get_pid()

		if pid is not None:
			# Is the process stilll running?
			if os.path.isdir(f"/proc/{pid}"):
				return True
			else: 
				# The process no longer exists, clean up the old files
				self._cleanup()
	
	def _cleanup(self):
		try:
			os.remove(self._PIDFILE)
		except:
			pass

	def add_host_to_switch_db(self, vlan, mac, port):
		# Check if mac address belongs to a host we manage
		rows = self._command.db.select(f"""
		n.name
		from nodes n, networks ns
		where ns.mac = '%s'
		and ns.node = n.id
		""" % mac)
			
		for host, in rows:
			for row in self._command.call("list.switch.host", [self.switchname]):
				if row['port'] == int(port):
					self._logger.info("port is already known: %s %s" % (self.switchname, port))
					break
			else:
				result = subprocess.run([
				"/opt/stack/bin/stack",
				"add",
				"switch",
				"host",
				self.switchname,
				f"host={host}",
				f"port={port}",
				f"vlan={vlan}",
				])


