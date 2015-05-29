#!@PYTHON@

import os,sys
import socket
import stack.app

class App(stack.app.Application):

	def __init__(self, argv):
		stack.app.Application.__init__(self,argv)
		
		self.usage_name = 'Check Port'
		self.usage_version = '4.2'

		self.node_name = 'localhost'
		self.port_num = 5901
		
		nodehelp = '(nodename default=%s)' % self.node_name
		porthelp = '(port number default=%d)' % (self.port_num)
		self.getopt.l.extend([ ('node=',nodehelp),('port=',porthelp) ])
		self.getopt.s.extend([('n:',nodehelp),('p:',porthelp)])
		return

	def parseArg(self, c):
		stack.app.Application.parseArg(self,c)

		key, val = c
		if key in ('--port'):
			self.port_num = int(val)
		elif key in ('--node'):
			self.node_name = val

		return

	def run(self):
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		try:
			s.connect((self.node_name,self.port_num))
		except:
			print 'closed'
			sys.exit(1)
		
		print 'open'
		s.close()
		sys.exit(0)
	
app = App(sys.argv)
app.parseArgs()
app.run()

