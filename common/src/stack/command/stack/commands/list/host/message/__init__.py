# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import json
import signal
import zmq
import pprint
import stack.mq
import stack.commands.sync.host


class Subscriber(stack.mq.Subscriber):
	def __init__(self, context, channel, host):
		stack.mq.Subscriber.__init__(self, context, host)
		self.host = host
		self.subscribe(channel)

	def callback(self, message):
		c = message.getChannel()
		i = message.getID()
		h = message.getHops()
		s = message.getSource()

		print()
		msg_info = '%s: publisher=%s' % (message.getTime(), self.host) 
		if s:
			msg_info = msg_info + ' source=%s' % s
		if c:
			msg_info = msg_info + ' channel=%s' % c
		if i:
			msg_info = msg_info + ' id=%d' % i
		if h:
			msg_info = msg_info + ' hops=%d' % h

		print(msg_info)
		p = pprint.PrettyPrinter()
		m = message.getMessage()
		try:
			o = json.loads(m)
		except:
			o = m
		p.pprint(o)



class Command(stack.commands.sync.host.command):
	"""
	Attaches to one or more hosts' Message Queue and displays
	all messages on the provided channel(s).

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, listen
	to all host Message Queues.
	</arg>

	<param type='string' name='channel' optional='1'>
	Name of the channel, if not provided listen to all channels.
	</param>
	
	<example cmd='list host message backend-0-0 channel=debug'>
	Listen to the debug channel on backend-0-0
	</example>
	"""

	def handler(self, signal, frame):
		pass

	def run(self, params, args):

		(channel, ) = self.fillParams([
				('channel', '')
				])

		context = zmq.Context()
		hosts = self.getHostnames(args)
		run_hosts = self.getRunHosts(hosts)
		for h in run_hosts:
			host = h['name']
			subscriber = Subscriber(context, channel, host)
			subscriber.setDaemon(True)
			subscriber.start()

		signal.signal(signal.SIGINT, self.handler)
		signal.pause()

			

