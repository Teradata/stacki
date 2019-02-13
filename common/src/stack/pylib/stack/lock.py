# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import fcntl


class Semaphore:
	"""
	Used to manage a on disk semaphore. No locking
	is provided.
	"""

	def __init__(self, path):
		self.path = path

	def read(self):
		try:
			fin = open(self.path, 'r')
		except:
			return None
		try:
			count = int(fin.read())
			fin.close()
		except:
			return None
		return count

	def write(self, count):
		try:
			fout = open(self.path, 'w')
		except:
			return None

		fout.write('%d' % count)
		fout.close()


class Mutex:
	"""
	Used the acquire and release a on disk mutex
	"""
     
	def __init__(self, path):
		self.path = path
		self.file = open(path, 'w')

	def __del__(self):
		self.release()
		self.file.close()
    
	def acquire(self):
		fcntl.flock(self.file, fcntl.LOCK_EX)

	def acquire_nonblocking(self):
		retval = 0
		try:
			fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
		except:
			retval = 1

		return retval
        
	def release(self):
		fcntl.flock(self.file, fcntl.LOCK_UN)
       
