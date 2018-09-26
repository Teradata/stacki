# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import socket
import stack.mq
import stack.commands.add.host


class Command(stack.commands.add.host.command):
	"""
	Adds a message to one or most host Message Queues

	<arg type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, the
	message is sent to all hosts.
	</arg>

	<param type='string' name='message' optional='0'>
	Message text
	</param>

	<param type='string' name='channel'>
	Name of the channel
	</param>

	<example cmd='add host message backend-0-0 message="hello world" channel=debug'>
	Sends "hello world" over the debug channel using the Message
	Queue on backend-0-0.
	</example>

	"""

	def run(self, params, args):
		hosts = self.getHosts(args)

		(channel, ttl, message, source) = self.fillParams([
			('channel', 'debug', False),
			('ttl', None, False),
			('message', None, True),
			('source', None, False)
		])

		try:
			ttl = int(ttl)
		except TypeError:
			pass # already set to None
		except ValueError:
			ttl = None

		for host in hosts:
			tx  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			msg = stack.mq.Message(message, channel=channel, ttl=ttl, source=source)

			if host == self.db.getHostname('localhost'):
				host = 'localhost'

			tx.sendto(str(msg).encode(), (host, stack.mq.ports.publish))
			tx.close()
