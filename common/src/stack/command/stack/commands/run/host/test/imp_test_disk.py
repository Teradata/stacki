# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


import rocks.commands
import salt.client
import salt.runner
import salt.config
import re
import random
import os, sys
import time

class Implementation(rocks.commands.Implementation):
	def run(self, args):
		hosts, extras = args

		self.owner.fields = [ "host", "disk", "KB/s (read)",
			"KB/s (write)" ]

		__opts__ = salt.config.client_config("/etc/salt/master")

		# Create the salt local client and runner client objects.
		# The LocalClient is responsible for starting the job on
		# a compute node
		self.salt = salt.client.LocalClient()

		# The runner client is responsible for managing the running
		# job
		self.runner = salt.runner.RunnerClient(__opts__)

		# Data structures
		self.host_dict = {}
		self.populate_host_dict(hosts)
		self.running_jobs = {}
		self.running_hosts = {}
		self.host_output = {}

		# Lambda function to filter out hosts that have completed
		# running the disk tests on all their disks
		f = lambda x: len(x[1]) > 0

		free_hosts = self.host_dict.keys()
		if len(free_hosts) == 0:
			#
			# nothing to do
			#
			done = True
		else:
			done = False

		self.close_out()
		while not done:
			# Get a list of free hosts. Start with the full list
			# of hosts
			free_hosts = self.host_dict.keys()
			while len(free_hosts) > 0:
				host = free_hosts.pop()

				if self.host_dict.has_key(host) and \
						len(self.host_dict[host]) > 0:

					# Run the test
					self.run_salt_job(host,
						self.host_dict[host])

					self.host_dict[host] = {}

			# Check if the list of active jobs is the same as our
			# book-keeping
			if len(self.active_jobs()) == len(self.running_jobs):
				time.sleep(1)
				continue

			# If jobs have ended, get a list of all jobs
			# that are complete.
			for jid in self.running_jobs.keys():
				if self.is_job_active(jid):
					pass
				else:
					# Get the host that a job is running on
					host = self.running_jobs[jid]

					# Clean up the book-keeping
					self.running_jobs.pop(jid)
					i = self.running_hosts[host].index(jid)
					self.running_hosts[host].pop(i)

					# Get the output for the job ID
					joboutput = self.get_job_output(jid)
					if joboutput and \
						host in joboutput.keys():

						self.host_output[host] = \
							joboutput[host]
					else:
						self.host_output[host] = {}

			# Clean up the host dictionary to remove hosts that
			# have all their tests complete
			self.host_dict = dict(filter(f,
				self.host_dict.iteritems()))

			# Check to see if we're finished with all tests and
			# all hosts
			if len(self.running_jobs) == 0 and \
					len(self.host_dict) == 0:
				done = True


		self.open_out()

		# Format the host specific output to be consumable
		for host in self.host_output:
			keys = self.host_output[host].keys()
			keys.sort()
			for disk in keys:
				o = self.host_output[host][disk]
				self.owner.addOutput(host, (disk,
					o['read_bw'],
					o['write_bw']))

	def active_jobs(self):
		active_jobs = self.runner.cmd("jobs.active",[])
		job_id_list = active_jobs.keys()
		return job_id_list
		
	def run_salt_job(self, host, tests):
		jid = self.salt.cmd_async(host, 'fio.run', [ tests ],
			expr_form="list")

		tries = 5
		while tries > 0:
			if not self.is_job_active(jid):
				time.sleep(1)
				tries -= 1 
			else:
				tries = 0

		self.running_jobs[jid] = host

		if not self.running_hosts.has_key(host):
			self.running_hosts[host] = []
		self.running_hosts[host].append(jid)

	def is_job_active(self, jid):
		job_id_list = self.active_jobs()
		if jid in job_id_list:
			return True
		else:
			return False

	def is_job_complete(self, jid):
		return not self.is_job_active(jid)

	def get_job_output(self, jid):
		output = self.runner.cmd("jobs.lookup_jid", [jid])
		return output
		
	def get_disks(self, host):
		out = self.owner.call("list.host.partition", [host])
		disks = []
		parts = []
		root_disk = None
		disk_re = re.compile("[a-z]+([0-9][0-9])*")
		for o in out:
			if o["mountpoint"] == "" and \
					o["type"] == "":
				disks.append(o["device"])
				continue

			if o["mountpoint"] == "/":
				dev = o["device"]
				s = disk_re.match(dev)
				root_disk = s.group(0)
				continue

		try:
			rd_index = disks.index(root_disk)
			disks.pop(rd_index)
		except ValueError:
			pass

		for o in out:
			if o["mountpoint"] == "":
				continue

			dev = o["device"]
			s = disk_re.match(dev)
			if s:
				#
				# skip software RAID devices
				#
				if s == 'md':
					continue

				raw_dev = s.group(0)
				if raw_dev == root_disk:
					continue

				#
				# if a disk has multiple partitions, this will
				# only test one partition on the disk. no
				# need to test multiple partitions on the same
				# disk.
				#
				if raw_dev in disks:
					mnt = o["mountpoint"]
					if mnt and mnt[0] == '/':
						parts.append((mnt, raw_dev))
		
				try:
					d_index = disks.index(raw_dev)
					disks.pop(d_index)
				except ValueError:
					pass

		return (disks, parts)
				
	def close_out(self):
		sys.stdout.flush()
		sys.stderr.flush()
		self._stdout_bak = os.dup(1)
		self._stderr_bak = os.dup(2)

		_devnull = open("/tmp/hwtest.log",'a+')
		os.dup2(_devnull.fileno(), 1)
		os.dup2(_devnull.fileno(), 2)

		sys.stdout.flush()

	def open_out(self):
		sys.stdout.flush()
		sys.stderr.flush()

		os.dup2(self._stdout_bak, 1)
		os.dup2(self._stderr_bak, 2)

	def populate_host_dict(self, hosts):
		for host in hosts:
			disks, parts = self.get_disks(host)
			self.host_dict[host] = []
			for disk in disks:
				self.host_dict[host].append(
					('rawdisk', "/dev/%s" % disk, disk))
			for part, disk in parts:
				self.host_dict[host].append(
					('mountpoint', part, disk))

		f = lambda x: len(x[1]) > 0
		self.host_dict = dict(filter(f, self.host_dict.iteritems()))


