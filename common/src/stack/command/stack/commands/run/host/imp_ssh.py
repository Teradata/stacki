# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import threading
import time
from stack.commands.run.host import Parallel

class Implementation(stack.commands.Implementation):

	#@warningLicenseCheck
	def run(self, args):
		# Command to run
		cmd = self.owner.cmd

		# Hosts to run the commands on
		hosts = self.owner.run_hosts

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
				host = hosts[i]['host']
				hostname = hosts[i]['name']

				host_output[host] = {'output': None, 'retval': -1}
				p = Parallel(cmd, hostname, host_output[host], timeout)
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

