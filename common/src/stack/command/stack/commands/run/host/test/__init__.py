# @copyright@
# Copyright (c) 2006 - 2014 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @copyright@


import os
import stack.commands
import json
import sys
from stack.exception import *

class Command(stack.commands.Command, stack.commands.HostArgumentProcessor):
	"""
	Run tests on hosts. This is commonly used to "validate" the
	hardware for a cluster.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, the command
	is run on all 'managed' hosts. By default, all compute nodes are
	'managed' nodes. To determine if a host is managed, execute:
	'stack list host attr hostname | grep managed'. If you see output like:
	'compute-0-0: managed true', then the host is managed.
	</arg>

	<param type='string' name='test' optional='0'>
	The test(s) to run. Valid tests are: "memory", "disk", "network" and
	"all".
	If "all", then run "memory", "disk" and "network" tests on the hosts.
	</param>

	<param type='string' name='extras'>
	Test-specific parameter.
	For the "all" test, this will be the filename prefix used to store
	the test results. All test results will append ".{test}" to the prefix,
	e.g., if "extras" is "/export/mytest", then the memory test results will
	be stored in the file "/export/mytest.memory". Default: "/tmp/test".
	For the "network" test, this is an optional parameter that can be
	used to specify which "network" to test. To get a list of networks,
	execute "stack list network". Default: "private".
	</param>

	<param type='string' name='status'>
	Determine if "stack run host test" is already running. If it is,
	output "is running". If there are no other instances of "stack run
	host test" running, then output "is not running".
	</param>

	<example cmd='run host test compute-0-0 test="memory"'>
	Run the "memory" test on compute-0-0.
	</example>

	<example cmd='run host test compute test="all" extras="/tmp/test"'>
	Run all the tests on all the compute nodes and store the results in
	"/tmp/test.memory", "/tmp/test.disk" and "/tmp/test.network".
	</example>
	"""

	fields = None

	def is_running(self, pidFile):
		status = False

		if os.path.exists(pidFile):
			#
			# Make sure process is actually running, and
			# that the file simply isn't left over from a
			# previously killed process
			#
			file = open(pidFile, 'r')

			try:
				pid = int(file.readline().strip())
				os.getpgid(pid)
				status = True
			except:
				pass

			if not status:
				os.unlink(pidFile)

		return status


	def run(self, params, args):
		pidFile = '/var/run/stack-run-host-test.pid'
		allpidFile = '/var/run/stack-run-host-test-all.pid'

		hosts = self.getHostnames(args, managed_only = 1)

		(test_type, extras, status) = self.fillParams([
			('test', None), ('extras', None), ('status', 'n')])

		if self.str2bool(status):
			if self.is_running(pidFile) or \
					self.is_running(allpidFile):
				print('is running')
			else:
				print('is not running')

			return

		if not test_type:
			raise ParamRequired(self,'test')

		if test_type not in [ 'disk', 'memory', 'network', 'all' ]:
			print(dir(stack.exception))
			raise ParamValue(self,'test', '"disk", "memory", "network", or "all"')

		if test_type == 'all':
			file = open(allpidFile, 'w')
			file.write("%d\n" % os.getpid())
			file.close()

		file = open(pidFile, 'w')
		file.write("%d\n" % os.getpid())
		file.close()

		self.beginOutput()

		args = (hosts, extras)
		self.runImplementation('test_%s' % test_type, args)

		self.endOutput(header = self.fields, trimOwner = False)

		#
		# we need this because of the 'all' test, since the 'all' test
		# calls 'stack run host test' for the disk, network and memory
		# test. That is, it will call this function and each time it
		# will remove the pidFile.
		#
		if os.path.exists(pidFile):
			os.unlink(pidFile)

		if os.path.exists(allpidFile):
			os.unlink(allpidFile)

