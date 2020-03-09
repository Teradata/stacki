# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: failure_report
    type: aggregate
    short_description: Report formatted output of failed tasks
    description:
      - Displays a report of failed tasks
      - Outputs STDOUT and STDERR of shell tasks in a nice way
'''

from collections import defaultdict

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
	"""
	Gather up failed tasks and report the output in a formatted way
	"""

	CALLBACK_VERSION = 2.0
	CALLBACK_TYPE = 'aggregate'
	CALLBACK_NAME = 'failure_report'
	CALLBACK_NEEDS_WHITELIST = True

	def __init__(self, *args, **kwargs):
		super(CallbackModule, self).__init__(*args, **kwargs)

		self.failed_tasks = defaultdict(list)

	def v2_runner_on_failed(self, result, ignore_errors=False):
		self.failed_tasks[result._host.get_name()].append(result)

	def v2_playbook_on_stats(self, stats):
		if not self.failed_tasks:
			# Nothin' to report
			return

		# Stuff done failed. Report the output in a nicely formatted way.
		self._display.banner("FAILED TASKS")

		for host in sorted(self.failed_tasks):
			self._display.banner("HOST [%s]" % host, color="blue")

			for result in self.failed_tasks[host]:
				self._display.banner("TASK [%s]" % result._task.name)

				# Failure message
				if "msg" in result._result:
					self._display.display("error: %s" % result._result["msg"], color="red")

				# Return code, if this was a shell task
				if "rc" in result._result:
					self._display.display("return: %s" % result._result["rc"])

				# Stdout, indented nicely
				if "stdout_lines" in result._result:
					stdout = "\n        ".join(result._result["stdout_lines"])
					self._display.display("stdout: %s" % stdout)

				# Stderr, indented nicely
				if "stderr_lines" in result._result:
					stderr = "\n        ".join(result._result["stderr_lines"])
					self._display.display("stderr: %s" % stderr)

		self._display.display("\n")
