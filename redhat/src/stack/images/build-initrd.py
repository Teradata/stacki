#!/opt/stack/bin/python3
#
# @copyright@
# @copyright@
#
# @rocks@
# @rocks@

import os
import os.path
import stack.bootable
from stack.exception import CommandError

import argparse

class App():
	def __init__(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('--rpms', help='Path to Local RPMs')
		parser.add_argument('--pkgs', help='RPM packages to add to initrd.img')
		parser.add_argument('--update-pkgs', help='RPM packages to add to /updates in initrd.img')
		parser.add_argument('--build-directory', help='Directory to apply all RPMs to')
		args = parser.parse_args()
		self.rpms = args.rpms
		self.pkgs = args.pkgs.split()
		self.update_pkgs = args.update_pkgs.split()
		self.build_directory = args.build_directory


	def overlaypkgs(self, pkgs, update):
		for pkg in pkgs:
			RPM = self.boot.findFile(pkg)
			if not RPM:
				raise CommandError(self, "Could not find %s rpm" % pkg)

			print("Applying package %s" % pkg)

			self.boot.applyRPM(RPM, 
				os.path.join(os.getcwd(), pkg),
					flags='--noscripts --excludedocs')

			# now 'overlay' the package onto the expanded initrd
			destdir = '../%s' % self.build_directory
			if update:
				destdir = '%s/updates' % destdir

			os.system('cd %s ; find . -not -type d | cpio -pdu %s'
				% (pkg, destdir))


	def run(self):
		print("build-initrd starting...")

		self.boot = stack.bootable.Bootable(self.rpms, self.build_directory)

		print('updatepkgs: ' , self.update_pkgs)
		print('pkgs      : ' , self.pkgs)

		self.overlaypkgs(self.update_pkgs, True)
		self.overlaypkgs(self.pkgs, False)

		print("build-initrd complete.")


app = App()
app.run()
