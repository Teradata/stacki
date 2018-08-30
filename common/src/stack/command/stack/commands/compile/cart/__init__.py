# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import os
import grp
import stat
import shutil
import subprocess
import stack.commands
import stack.lock


class Command(stack.commands.CartArgumentProcessor,
	stack.commands.compile.command):
	"""
	Compile a repo inside the cart so it can be used by backend nodes
	for installation.
	
	<arg optional='1' type='string' name='cart' repeat='1'>
	List of carts. This should be the cart base name (e.g., stacki, os,
	etc.). If no cart names are specified, then compiles repos for all
	known carts.
	</arg>

	<example cmd='compile cart devel'>		
	Compile a repo for the devel cart.
	</example>
	"""		

	def doRepo(self, cart):
		#
		# compile a repo for the cart, but only if the cart has been
		# changed since the last time we ran this command
		#
		cartpath = '/export/stack/carts/%s' % cart
		repodata = os.path.join(cartpath, 'repodata')
		fingerprint = os.path.join(cartpath, 'fingerprint')
		existingfinger = {}

		if os.path.exists(fingerprint):
			file = open(fingerprint)
			for line in file.readlines():
				l = line.split()
				if len(l) == 3:
					fname = l[0].strip()
					fsize = l[1].strip()
					fmtime = l[2].strip()	

					existingfinger[fname] = {
						'size'  : fsize, 
						'mtime' : fmtime }
			file.close()

		newfinger = {}

		for dirpath, dirnames, filenames in os.walk(cartpath):
			#
			# ignore 'repodata' directory
			#
			if dirpath == repodata:
				continue

			for file in filenames:
				#
				# ignore the 'fingerprint' file
				#
				if file == 'fingerprint':
					continue

				filepath = os.path.join(dirpath, file)
				filestat = os.stat(filepath)
				fsize = '%d' % filestat.st_size
				fmtime = '%d' % filestat.st_mtime

				#
				# always populate 'newfinger' 
				#
				newfinger[filepath] = {
					'size' : fsize, 
					'mtime' : fmtime }
				
		#
		# now figure out if the cart has changed since the last time
		# the fingerprint was calculated
		#
		gr_name, gr_passwd, gr_gid, gr_mem = grp.getgrnam('apache')

		if existingfinger != newfinger:
			#
			# make sure apache can write in the carts directory
			# before we open the fingerprint file
			#
			try:
				os.chown(cartpath, -1, gr_gid)
			except:
				pass

			perms = os.stat(cartpath)[stat.ST_MODE]
			perms = perms | stat.S_IRGRP | stat.S_IXGRP \
				| stat.S_IWGRP

			try:
				os.chmod(dirpath, perms)
			except:
				pass

			file = open(fingerprint, 'w')

			#
			# make sure apache can write this file
			#
			perms = os.stat(fingerprint)[stat.ST_MODE]
			perms = perms | stat.S_IRGRP | stat.S_IWGRP
			try:
				os.chmod(fingerprint, perms)
			except:
				pass

			for filename in newfinger.keys():
				file.write('%s %s %s\n' % (filename,
					newfinger[filename]['size'],
					newfinger[filename]['mtime']))
			file.close()

			#
			# rebuild the repodata
			#
			cwd = os.getcwd()
			os.chdir(cartpath)

			if os.path.exists(repodata):
				shutil.rmtree(repodata)
			subprocess.call([ 'createrepo', '.' ])

			os.chdir(cwd)

		#
		# make sure apache can read all the files and directories
		#
		for dirpath, dirnames, filenames in os.walk(cartpath):
			try:
				os.chown(dirpath, -1, gr_gid)
			except:
				pass

			perms = os.stat(dirpath)[stat.ST_MODE]
			perms = perms | stat.S_IRGRP | stat.S_IXGRP

			#
			# apache needs to be able to write in the cart
			# and repodata directores when carts are compiled on
			# the fly
			#
			if dirpath in [ cartpath, repodata ]:
				perms |= stat.S_IWGRP
			try:
				os.chmod(dirpath, perms)
			except:
				pass

			for file in filenames:
				filepath = os.path.join(dirpath, file)

				try:
					os.chown(filepath, -1, gr_gid)
				except:
					pass

				perms = os.stat(filepath)[stat.ST_MODE]
				perms = perms | stat.S_IRGRP

				#
				# apache needs to be able to write all files
				# in the repodata directory
				#
				if dirpath == repodata:
					perms = perms | stat.S_IWGRP
				try:
					os.chmod(filepath, perms)
				except:
					pass


	def run(self, params, args):
		for cart in self.getCartNames(args):
			#
			# ensure only one process can update the cart at a time
			#
			mutexfile = '/var/tmp/cart.%s.mutex' % cart
			mutex = stack.lock.Mutex(mutexfile)

			gr_name, gr_passwd, gr_gid, gr_mem = \
				grp.getgrnam('apache')
			try:
				os.chown(mutexfile, -1, gr_gid)
			except:
				pass

			perms = os.stat(mutexfile)[stat.ST_MODE]
			perms = perms | stat.S_IRGRP | stat.S_IWGRP

			try:
				os.chmod(mutexfile, perms)
			except:
				pass

			retval = mutex.acquire_nonblocking()
			if retval == 0:
				self.doRepo(cart)
				mutex.release()

