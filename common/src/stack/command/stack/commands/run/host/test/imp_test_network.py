# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.commands.sync.host import Parallel
from stack.commands.sync.host import timeout

class Implementation(stack.commands.Implementation):

	def tournament(self, hosts, subnet):
		if len(hosts) % 2:
			hosts.append('bye')

		rounds = []
		for i in range(0, len(hosts) - 1):
			if i == 0:
				h = hosts[0:int(len(hosts)/2)]
				a = hosts[int(len(hosts)/2):]
			else:
				h = [home[0]]
				h.append(away[0])
				for j in range(1,len(home) - 1):
					h.append(home[j])

				a = []
				for j in range(1,len(away)):
					a.append(away[j])
				a.append(home[-1])

			home = h
			away = a

			homehosts = []
			awayhosts = []
			for i in range(0, len(home)):
				if home[i] == 'bye' or away[i] == 'bye':
					#
					# skip the 'bye' games
					#
					continue

				homehosts.append(home[i])

				#
				# only the "away" hosts need to be translated
				# into the correct network name
				#
				awayhosts.append(self.owner.db.getHostname(
					away[i], subnet))

			rounds.append((homehosts, awayhosts))

		return rounds

	def run(self, args):
		hosts, subnet = args

		self.owner.fields = [ "host", "to", "mbits/sec" ]

		if not subnet:
			subnet = 'private'
		#
		# first, start iperf on all nodes
		#
		# remove the bye if it's there
		if 'bye' in hosts:
			hosts.remove('bye')

		cmd = 'systemctl start iperf3.service'
		res = self.owner.command('run.host', hosts + [ 'command=' + "%s" % cmd])
		threads = []
		file = open('/tmp/nettest.debug', 'w')
		for homes, aways in self.tournament(hosts, subnet):
			file.write('home %s\n' % homes)
			file.write('away %s\n' % aways)
			for home in homes:
				for away in aways:
					iperf_cmd = '/opt/stack/sbin/iperf3.py '
					iperf_cmd += '%s %s' % (home,away)

					cmd = 'ssh -T -x %s "%s"' % (home, iperf_cmd)
					p = Parallel(cmd)
					threads.append(p)
					p.start()

					for thread in threads:
						thread.join(timeout)
					out = p.out['output']
					file.write('%s\n' % out)

				for host in out:
					if type(out) != type({}) or not \
						out.has_key(host) or \
						type(out[host]) != type({}) or not \
						out[host].has_key('away') or not \
						out[host].has_key('sent') or not \
						out[host].has_key('recv'):

						continue
	

					tohost = out[host]['away']
					fromhost = self.owner.db.getHostname(host,
						subnet)
	
					if subnet == 'private':
						# 
						# just output the short name, that is,
						# don't append the private domain
						# (e.g., ".local")
						# 
						tohost = self.owner.db.getHostname(
							tohost)
						fromhost = self.owner.db.getHostname(
							fromhost)
	
					sent = float(out[host]['sent']) / (1000 * 1000)
					recv = float(out[host]['recv']) / (1000 * 1000)
	
					self.owner.addOutput(fromhost, (tohost,
						'%.2f' % sent))
					self.owner.addOutput(tohost, (fromhost,
						'%.2f' % recv))
	
		file.close()
		# remove the bye if it's there
		if 'bye' in hosts:
			hosts.remove('bye')

		cmd = 'systemctl stop iperf3.service'
		res = self.owner.command('run.host', hosts + [ 'command=' + "%s" % cmd])
