# @copyright@
# @copyright@

import os
import stat
import stack.mq
import stack.mq.producers


class FileStreamer(stack.mq.producers.ProducerBase):
	"""
	Watches a line oriented log file and stream all new
	content.  This is effective the same as a tail -F,
	including protection against logrotate.
	"""

	def __init__(self, scheduler, sock):
		stack.mq.producers.ProducerBase.__init__(self, scheduler, sock)
		self.size = None
		self.fin  = None

	def filename(self):
		"""
		Returns the name of the file the steamer 
		will watch.
		"""
		return None

	def schedule(self):
		return 1

	def produce(self):
		if not self.fin:
			try:
				self.fin = open(self.filename(), 'r')
			except:
				return
		if self.size is None:
			try:
				self.size = os.stat(self.filename())[stat.ST_SIZE]
				self.fin.seek(self.size)
			except:
				self.size = 0

		# If the file shran the reset and open it again. This
		# happens when we get hit by logrotate or reseting
		# daemons.

		if os.stat(self.filename())[stat.ST_SIZE] < self.size:
			self.fin.close()
			self.fin  = None
			self.size = 0 # Start and beginning of new file
			return self.produce()

		list = None
		while True:
			where = self.fin.tell()
			line  = self.fin.readline()
			if not line:
				self.size = where
				break
			else:
				if not list:
					list = []
				list.append(line[:-1])
		return list








