import glob
import os
import re
import subprocess
import time

import pexpect
import pytest


class TestBossConfigSnack:
	DOWN_KEY = "\033[B"

	@pytest.fixture
	def mount_cdrom(self):
		# StackiOS test pipeline doesn't have a stacki ISO, so we skip the test
		if not glob.glob("/export/isos/stacki-*.iso"):
			pytest.skip("No stacki ISO available")

		subprocess.run("mount /export/isos/stacki-*.iso /mnt/cdrom", shell=True, check=True)

		yield

		subprocess.run("umount /mnt/cdrom", shell=True, check=True)

	@pytest.fixture
	def no_site_attrs(self):
		if os.path.exists("/tmp/site.attrs"):
			os.rename("/tmp/site.attrs", "/tmp/site.attrs.bak")

		yield

		if os.path.exists("/tmp/site.attrs.bak"):
			os.rename("/tmp/site.attrs.bak", "/tmp/site.attrs")

	@pytest.fixture
	def no_rolls_xml(self):
		if os.path.exists("/tmp/rolls.xml"):
			os.rename("/tmp/rolls.xml", "/tmp/rolls.xml.bak")

		yield

		if os.path.exists("/tmp/rolls.xml.bak"):
			os.rename("/tmp/rolls.xml.bak", "/tmp/rolls.xml")

	def test_minimal(self, host, host_os, mount_cdrom, no_site_attrs, no_rolls_xml, test_file):
		# Launch the wizard and walk through it
		env = os.environ.copy()
		env["TERM"] = "linux"
		wizard = pexpect.spawn(
			"/opt/stack/bin/boss_config_snack.py --no-partition --no-net-reconfig",
			env=env
		)

		# Set the timezone to Denver
		wizard.expect("Cluster Timezone")
		wizard.send(self.DOWN_KEY+"\t\r")

		# Fill out the network info
		wizard.expect("Network")
		wizard.send("test.example.com\t")
		wizard.send(self.DOWN_KEY+"\t")
		wizard.send("192.0.2.2\t")
		wizard.send("255.255.255.0\t")
		wizard.send("192.0.2.1\t")
		wizard.send("1.1.1.1\t\r")

		# Fill out the password
		wizard.expect("Password:")
		wizard.send("test\t")
		wizard.send("test\t\r")

		# Select the default pallet
		wizard.expect("Pallets to Install")
		wizard.send("\t\r")

		# Select Finish
		wizard.expect("Summary")
		wizard.send("\t\r")

		# Wait for the wizard to finish
		wizard.expect(pexpect.EOF, timeout=2)

		# Read the site.attrs created
		with open("/tmp/site.attrs") as f:
			site_attrs_generated = f.read()

		# Make sure the mac address is a valid format, then remove it
		site_attrs_generated, cnt = re.subn(
			r"Kickstart_PrivateEthernet:[0-9a-fA-F:]{17}",
			"Kickstart_PrivateEthernet:",
			site_attrs_generated
		)
		assert cnt == 1

		# Make sure the password is a valid format, then remove it
		site_attrs_generated, cnt = re.subn(
			r"Kickstart_PrivateRootPassword:\$6\$[a-zA-Z0-9./]+\$[a-zA-Z0-9./]+",
			"Kickstart_PrivateRootPassword:",
			site_attrs_generated
		)
		assert cnt == 1

		# Get the expected site.attrs
		with open(test_file(f"wizard/boss_config_snack_minimal_site.attrs")) as f:
			site_attrs_expected = f.read()

		assert site_attrs_generated == site_attrs_expected

		# Read the rolls.xml created
		with open("/tmp/rolls.xml") as f:
			rolls_xml_generated = f.read()

		# Check that the rolls.xml got generated correctly as well
		assert re.fullmatch(
			r'<rolls><roll arch="x86_64" diskid="" '
			r'name="stacki" release="[^"]+" url="http://127.0.0.1/mnt/cdrom/" '
			r'version="[^"]+" /></rolls>',
			rolls_xml_generated
		) is not None
