#
# @SI_Copyright
# @SI_Copyright
#

import stack.commands

class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
	List the Cluster Hosts Summary
	"""

	def run_cmd(self, cmd):
		cmd_args = ['command=%s' % cmd,'output-format=binary']
		cmd_args.extend(self.hosts)
		s = self.call("run.host", cmd_args)
		host_out = {}

		cur_host = None
		cur_out = []
		for i in s:
			prev_host = cur_host
			cur_host = i['col-0']
			if prev_host != None and prev_host != cur_host:
					host_out[prev_host] = '\n'.join(cur_out)
					cur_out = []
			if i['col-1'].startswith('Warning: '):
				continue
			cur_out.append(i['col-1'])

		host_out[cur_host] = '\n'.join(cur_out)
		
		return host_out


	def run(self, params, args):
		self.hosts = self.getHostnames(args)
		self.beginOutput()
		
		self.runPlugins()

		self.endOutput()
