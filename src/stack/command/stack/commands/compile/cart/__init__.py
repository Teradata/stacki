# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@

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
						'size' : fsize, 
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
			# directory when carts are compiled on the fly
			#
			if dirpath == cartpath:
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

				try:
					os.chmod(filepath, perms)
				except:
					pass


	def run(self, params, args):
		for cart in self.getCartNames(args, params):
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

