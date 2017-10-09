# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import threading
import socket
import time
import subprocess


class Implementation(stack.commands.Implementation):

	#@warningLicenseCheck
	def run(self, args):
		# Command to run
		cmd = self.owner.cmd

		# Hosts to run the commands on
		hosts = self.owner.hosts

		# Dictionary to store output
		host_output = {}

		# Control Collation
		collate = self.owner.collate

		# Number of simultaneous threads allowed
		numthreads = self.owner.numthreads

		# Delay between starting threads.
		delay = self.owner.delay

		# Timeout that controls when to terminate SSH
		timeout = self.owner.timeout

		threads = []


		# If we haven't set the number of threads
		# to run concurrently, don't check for
		# running threads.
		if numthreads == 0:
			running_threads = -1
		else:
			running_threads = 0
		work = len(hosts)
		i = 0
		while work:
			# Run the first batch of threads
			while running_threads < numthreads and i < len(hosts):
				host = hosts[i]

				host_output[host] = {'output': None, 'retval': -1}
				p = Parallel(cmd, host, host_output[host], timeout)
				p.setDaemon(True)
				p.start()
				threads.append(p)	

				# Increment number of running threads, only if
				# there is a maximum number of allowed threads
				if numthreads > 0:
					running_threads += 1
				i += 1	

				if delay > 0:
					time.sleep(delay)

			# Collect completed threads
			try:
				active = threading.enumerate()

				t = threads
				for thread in threads:
					if thread not in active:
						thread.join(0.1)
						threads.remove(thread)
						# As threads exit, decrement the
						# number of running threads.
						running_threads -= 1
						work -= 1

				# If we're running fewer threads
				# than maximum allowed, continue
				# to create newer threads
				if running_threads < numthreads:
					continue

				# If not, don't burn the CPU
				time.sleep(0.5)


			except KeyboardInterrupt:
				work = 0

		# Gather and print the output
		for host in host_output:
			if not collate:
				if host_output[host]['output']:
					print(str(host_output[host]['output']))
			else:
				if isinstance((host_output[host]['output']), bytes):
					out = (host_output[host]['output']).decode('utf').split('\n')
				else:
					out = (host_output[host]['output']).split('\n')
				for line in out:
					self.owner.addOutput(host, line)



class Parallel(threading.Thread):
	def __init__(self, cmd, host, output, timeout):
		threading.Thread.__init__(self)
		self.cmd = cmd
		self.host = host
		self.output = output
		self.timeout = timeout

	def run(self):
		"""
		Runs the COMMAND on the remote HOST.  If the HOST is the
		current machine just run the COMMAND in a subprocess.
		"""
		
		online = True

		if self.host != socket.gethostname().split('.')[0]:
			# First check to make the machine is up and SSH is responding.
			#
			# This catches the case when the node is up, sshd is sitting 
			# on port 22, but it is not responding (e.g., the node is 
			# overloaded, sshd is hung, etc.)
			#
			# sock.recv() should return something like:
			#
			#	SSH-2.0-OpenSSH_4.3

			sock   = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.settimeout(2.0)
			try:
				sock.connect((self.host, 22))
				buf = sock.recv(64)
			except:
				online = False

		# If we're online, run the SSH command. Make sure to
		# pipe STDERR to STDOUT. We wan't to merge the streams
		# as if this were the output of running the command on
		# the command line.
		if online:
			proc = subprocess.Popen([ 'ssh', self.host, self.cmd ],
						stdin=None,
						stdout=subprocess.PIPE,
						stderr=subprocess.STDOUT)

			# If we dont have a timeout, just wait for the process
			# to finish
			if self.timeout <= 0:
				retval = proc.wait()
			else:
				hit_timeout = False
				start_time = time.time()
				while hit_timeout is False:
					# Check if process is done
					retval = proc.poll()
					if retval is not None:
						break
					# If we're not done, check if we're out
					# of time.
					if time.time() - start_time > self.timeout:
						hit_timeout = True
						break
					# If we're not done, and not timed out yet,
					# just wait
					if retval is None:
						time.sleep(0.25)
			
				# If we hit a timeout, terminate, and
				# get return code
				if hit_timeout is True:
					proc.terminate()
					retval = proc.wait()

			# Finally get the output, and return back
			o, e = proc.communicate()
			self.output['retval'] = retval
			self.output['output'] = o.strip()

		else:
			# If we couldn't connect to the host,
			# return back
			self.output['retval'] = -1
			self.output['output'] = 'down'

		return
