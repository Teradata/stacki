# @copyright@
# @copyright@

import os
import shutil
import subprocess
import tempfile
import time
import stack.commands
from stack.exception import CommandError, UsageError, ArgUnique

class command(stack.commands.ImageArgumentProcessor,
	      stack.commands.NFSRootArgumentProcessor,
	      stack.commands.OSArgumentProcessor,
	      stack.commands.add.command):
	pass


class Command(command):
	"""
	Create a nfsroot directory used to network boot diskless clients. 
	The is os specific and currently only supports raspbian, it also 
	doesn't scale so don't worry about this being just for the Pi.

	This code is very beta.

	<arg type='string' name='name'>
	Name of the new nfsroot volume.
	</arg>

	<param type='string' name='image' optional='0'>
	Name of the image off of which the nfsroot is based.
	</param>
	"""

	def run(self, params, args):

		image, = self.fillParams([('image', None, True)])

		if len(args) != 1:
			raise ArgUnique(self, 'name')
		nfsroot = args[0]

		images = self.getImageNames([image])
		if len(images) != 1:
			raise CommandError(self, 'specify only one image')
		image = images[0]

		if nfsroot in self.getNFSRootNames():
			raise CommandError(self, f'{nfsroot} already exists')

		# nfsroot  - used the name of this object
		# tftpboot - uses the name of the image
 
		for row in self.call('list.image', [ image ]):
			image_path = os.path.join('/export/stack/images', row['image'])
			image_os   = row['os']
			tftp = row['name']

		# I told you this way beta, Pis only for now.

		if image_os != 'raspbian':
			raise CommandError(self, 'only supports raspbian for nfsroot')

		nfsroot_path  = os.path.join('/export/stack/roots', nfsroot)
		tftp_path     = os.path.join('/tftpboot', tftp)

		if os.path.exists(nfsroot_path):
			raise CommandError(self, f'directory {nfsroot_path} already exists')
		if os.path.exists(tftp_path):
			print(f'directory {tftp_path} being replaced (shared image)')

		loop = None
		subprocess.run(['losetup', '-f', '-P', image_path])
		for line in subprocess.run(['losetup', '-l'], capture_output=True).stdout.decode().split('\n'):
			if line.find(image_path) > 0:
				tokens = line.split()
				loop = tokens[0]
		if not loop:
			raise CommandError(self, 'cannot mount image on loop device')

		def loop_rsync(device, dest):
			print('loop_rsync', device, dest)
			cwd = os.getcwd()
			tmp = tempfile.mktemp()
			os.makedirs(tmp)

			subprocess.run(['mount', device, tmp])
			os.chdir(tmp)
			os.system(f'rsync -xa . {dest}')
			os.chdir(cwd)
			subprocess.run(['umount', tmp])
			
			shutil.rmtree(tmp)

		# sync over nfsroot 
		loop_rsync(f'{loop}p2', f'{nfsroot_path}')
		loop_rsync(f'{loop}p1', f'{nfsroot_path}/boot')
		subprocess.run(['losetup', '-d', loop])

		# sync over tftpboot
		os.chdir(f'{nfsroot_path}/boot')
		os.system(f'rsync -xa . {tftp_path}')

		# enable ssh and copy over root's public key
		open(f'{nfsroot_path}/boot/ssh', 'a').close()
		ssh = os.path.join(nfsroot_path, 'root', '.ssh')
		if not os.path.exists(ssh):
			os.makedirs(ssh)
		os.system(f'cat /root/.ssh/id_rsa.pub > {ssh}/authorized_keys')
		os.system(f'chmod 600 {ssh}/authorized_keys')

		# fstab for /proc only (nfsroot the rest)
		fstab = os.path.join(nfsroot_path, 'etc', 'fstab')
		os.system(f'mv {fstab} {fstab}.bak')
		os.system(f'grep /proc {fstab}.bak > {fstab}')

		self.db.execute("""
			insert into nfsroots(name, os, tftp, nfs)
			values (%s, (select id from oses where name=%s), %s, %s)
			""", (nfsroot, image_os, tftp, nfsroot))



		
		
		
