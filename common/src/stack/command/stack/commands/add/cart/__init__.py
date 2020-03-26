# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import grp
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tarfile

from stack.bool import str2bool
import stack.commands
from stack.commands import CartArgProcessor
from stack.exception import ArgRequired, ArgUnique, CommandError, UsageError
from stack.download import fetch, FetchError

# if requests is not available, attempting to barnacle will fail
try:
        import requests
except ImportError:
        pass

class Command(CartArgProcessor, stack.commands.add.command):
	"""
	Add a cart. Files to download are concatenated
	from "url," "urlfile," and "authfile" options
	if any files are designated in the authfile.
	
	<arg type='string' name='cart' optional='1'>
	The name of the cart to be created.
	Can also be a URL to a cart that we would like to download and add.
	</arg>

	<param type='string' name='username'>
	If the remote cart download server requires authentication.
	</param>

	<param type='string' name='password'>
	If the remote cart download server requires authentication.
	</param>

	<param type='string' name='file'>
	Add a local cart from a compressed file.
	</param>

	<param type='string' name='url'>
	Add cart from a single url.
	</param>

	<param type='string' name='urlfile'>
	Add multiple carts from a textfile with urls.
	The urlfile is a simple newline-separated list of URLS
	</param>

	<param type='string' name='downloaddir'>
	Directory to download to. Defaults /tmp.
	</param>

	<param type='string' name='authfile'>
	Json formatted authentication file with Username and Password. This can also
	contain URLs for the cart. See examples below.
	</param>

	<param type='boolean' name='downloadonly'>
	If you just want to download them, set downloadonly=True.
	</param>

	<example cmd="add cart urlfile=/tmp/tdurls downloaddir=/export authfile=/root/carts.json">
	Download the carts in /tmp/tdurls into /export.
	Use the username/password in /root/carts.json.

	Example json looks like this:
	{
	"username":"myuserid",
	"password":"mypassword"
	}
	</example>
	<example cmd="add cart authfile=/root/carts.json">
	Specify Username, Password, and Cart URL information in the carts.json file.
	{
		"username":"myuserid",
		"password":"mypassword",
		"urlbase": "https://sdartifact.td.teradata.com/artifactory",
		"files": [ "pkgs-generic-snapshot-sd/stacki-5/kubernetes/kubernetes-stacki5-12.02.18.02.12-rc3.tgz" ]
	}
	</example>
	"""

	def fix_perms(self):
		# make sure apache can read all the files and directories
		# This is the atomic bomb change permissions because
		# it changes everything to root:apache in /export/stack/carts
		gr_name, gr_passwd, gr_gid, gr_mem = grp.getgrnam('apache')

		cartpath = '/export/stack/carts/'

		for dirpath, dirnames, cartfiles in os.walk(cartpath):
			try:
				os.chown(dirpath, -1, gr_gid)
			except:
				pass


			#
			# apache needs to be able to write in the cart directory
			# when carts are compiled on the fly
			#

			perms = os.stat(dirpath)[stat.ST_MODE]
			try:
				os.chmod(dirpath, perms | stat.S_IRWXG)
			except:
				pass

			for d in dirnames:
				p = os.path.join(dirpath, d)
				perms = os.stat(p)[stat.ST_MODE]
				try:
					os.chmod(dirpath, perms | stat.S_IRWXG)
				except:
					pass

			for f in cartfiles:
				filepath = os.path.join(dirpath, f)

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

	def check_cart(self,cartfile):
		req =  ['RPMS', 'graph', 'nodes']
		if tarfile.is_tarfile(cartfile) == True:
			with tarfile.open(cartfile,'r|*') as tar:
				files = tar.getmembers()
				dirs = [ os.path.split(f.name)[-1] \
					for f in files if f.isdir() == True ]
				if set(req).issubset(set(dirs)) == True:
					return True
				else:
					diff = set(req).difference(set(dirs))
					msg = "You're missing an %s " % diff
					msg += "dir in your cart"
					raise CommandError(self,msg)
					return False
		else:
			return False

	def unpack_cart(self, cart, cartfile, cartsdir):
		with tarfile.open(cartfile,'r|*') as tar:
			if self.check_cart(cartfile) == True:
				tar.extractall(cartsdir)
				return True
			else:
				print("That's no cart tarfile!")
				print("Removing %s" % cart)
				self.removeCart(cart)
				return False
		tar.close()

	def create_files(self, name, path):

		# write the graph file
		graph = open(os.path.join(path, 'graph', 'cart-%s.xml' % name), 'w')
		graph.write('<graph>\n\n')
		graph.write('\t<description>\n\t%s cart\n\t</description>\n\n' % name)
		graph.write('\t<order head="backend" tail="cart-%s-backend"/>\n' % name)
		graph.write('\t<edge  from="backend"   to="cart-%s-backend"/>\n\n' % name)
		graph.write('</graph>\n')
		graph.close()

		# write the node file
		node = open(os.path.join(path, 'nodes', 'cart-%s-backend.xml' % name), 'w')
		node.write('<stack:stack>\n\n')
		node.write('\t<stack:description>\n')
		node.write('\t%s cart backend appliance extensions\n' % name)
		node.write('\t</stack:description>\n\n')
		node.write('\t<stack:package><!-- add packages here --></stack:package>\n\n')
		node.write('<stack:script stack:stage="install-post">\n')
		node.write('<!-- add shell code for post install configuration -->\n')
		node.write('</stack:script>\n\n')
		node.write('</stack:stack>\n')
		node.close()

	def add_cart(self, cart, cart_url=None):
		# if the cart doesn't exist, add it to the database.
		if self.db.count('(ID) from carts where name=%s', (cart,)) == 0:
			self.db.execute("""
				insert into carts (Name, url) values (%s, %s)
				""", (cart, cart_url))

		# If the directory does not exist create it along with # a skeleton template.

		tree = Path(f'/export/stack/carts/{cart}')
		if not tree.is_dir():
			for subdir in ['RPMS', 'nodes', 'graph']:
				tree.joinpath(subdir).mkdir(mode=775, parents=True, exist_ok=True)

			self.create_files(cart, str(tree))

	def add_cart_file(self,cartfile, cart_url=None):
		cartsdir = '/export/stack/carts/'
		# if multiple suffixes, increment to remove
		# the right number to create the correct cart.
		comp_type = ['.gz', '.tgz', '.tar' ]
		suff = Path(cartfile).suffixes
		snum = 0
		for s in suff:
			if s in comp_type:
				snum += 1

		fbase = os.path.basename(cartfile).rsplit('.',snum)[0]
		# This fixes people's stupid.
		# take care of when the cart isn't packed right
		if Path(cartfile).is_file() == True:
			if tarfile.is_tarfile(cartfile) == True:
				with tarfile.open(cartfile,'r|*') as tar:
					tardir = tar.getnames()[0]
				tar.close()
			else:
				raise CommandError(self,"%s is not a tgz." % cartfile)
		else:
			raise CommandError(self,"%s does not exist." % cartfile)

		if tardir == fbase:
			cart = fbase
		elif tardir == 'RPMS':
			cart = fbase
			cartsdir = cartsdir + '%s' % fbase
		else:
			cart = tardir
		if cart_url:
			self.add_cart(cart, cart_url)
		else:
			self.add_cart(cart, cartfile)
		self.unpack_cart(cart, cartfile, cartsdir)

	def get_auth_info(self,authfile):
		if not os.path.exists(authfile):
			msg = '%s file not found' % authfile
			raise CommandError(self, msg)

		with open(authfile, 'r') as a:
			auth = json.load(a)

		if not auth:
			sys.stderr.write("Cannot read auth file %s\n" % \
				(authfile))
		try:
			base = auth['urlbase']
			urlfiles = auth['files']
			return(base,urlfiles,auth['username'],auth['password'])
		except:
			return(None,None,auth['username'],auth['password'])

	def get_urls(self, url, urlfile, dldir, authfile):
		urls = []
		if urlfile != None:
			with open(urlfile,'r') as f:
				urls = f.readlines()
			f.close()

		if url != None:
			urls.append(url)

		# check for urls in the json file
		if authfile:
			base, urlfiles, user, passwd = \
					self.get_auth_info(authfile)
		else:
			base = urlfiles = user = password = None

		# authfile might not have a base or urlfiles
		# we are requiring both.
		if base == None or urlfiles == None:
			pass
		else:
			for url in urlfiles:
				urls.append('%s/%s' % (base,url))
		return(urls)

	def download_url(self, url, dest, fname, user, password):
		r = requests.get(url, stream=True,
			auth=(user,password), timeout=5)
		if r.status_code == 200:
			with open(dest, 'wb') as f:
				shutil.copyfileobj(r.raw, f)
		else:
			raise CommandError(self, "Could not connect to server.")

	def run(self, params, args):
		cartfile, url, urlfile, dldir, authfile, donly, username, password = \
			self.fillParams([('file', None),
					('url', None),
					('urlfile', None),
					('downloaddir', '/tmp'),
					('authfile', None),
					('downloadonly', False),
					('username', None),
					('password', None),
					])

		#Validate username and password
		#need to provide either both or none
		if username and not password:
			raise UsageError(self, 'must supply a password with the username')
		if password and not username:
			raise UsageError(self, 'must supply a username with the password')

		carts = args
		cart_url = None
		# check if we are creating a new cart
		if url == urlfile == cartfile == authfile == None:
			if not len(carts):
				raise ArgRequired(self, 'cart')
			else:
				for cart in carts:
					# check if the cartfile is actally a url that we should download
					# if it is, we download it then set the cartfile to the local file
					if cart.startswith(('http://', 'ftp://', 'https://')):
						print(f'downloading {cart} ...')
						try:
							# passing True will display a % progress indicator in stdout
							cartfile = fetch(cart, username, password, True)
						except FetchError as e:
							raise CommandError(self, e)
						print('adding cart...')
						cart_url = cart
					else:
						self.add_cart(cart)

		# If there's a filename, check it.
		if cartfile == None:
			pass
		elif Path(cartfile).exists() == True \
			and Path(cartfile).is_file() == True:
		# If there is a filename, make sure it's a tar gz file.
			if self.check_cart(cartfile) == True:
				# if the file has not been downloaded from the internet
				# pass along the local path
				if not cart_url:
					cart_url = os.path.abspath(cartfile)
				self.add_cart_file(cartfile, cart_url)
				# now we cleanup the cart file if we donwloaded it
				if cart_url.startswith(('http', 'ftp')):
					p = subprocess.run(['rm', cartfile])
			else:
				msg = '%s is not a cart.' % cartfile
				raise CommandError(self,msg)
		else:
			msg = '%s was not found.' % cartfile
			raise CommandError(self,msg)

		# do the network cart if url or urlfile or authfile exist.
#			base,urlfiles,user,passwd = self.get_auth_info(authfile)
		if url != None or urlfile != None or authfile != None:
			if authfile != None:
				base,urlfiles,user,passwd = \
					self.get_auth_info(authfile)
			# then add_cart_file to them.
			urls = self.get_urls(url,urlfile,dldir,authfile)
			for url in urls:
				url = url.strip('\n')
				cartfile = os.path.basename(url)
				dest = '%s/%s' % (dldir,cartfile)
				self.download_url(url, dest, cartfile, user, passwd)
				if self.str2bool(donly) != True:
					self.add_cart_file(dest)

		# Fix all the perms all the time.
		self.fix_perms()
