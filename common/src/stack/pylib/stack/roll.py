#!/opt/stack/bin/python3
# 
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import xml.dom.minidom

class Generator():
	def __init__(self):
		self.rolls = []

	def parse(self, roll_file):
		'''
		parse a rolls.xml file.
		Note this is not the same as a roll-$PALLET.xml
		each call to parse resets rolls
		'''
		rolls = []

		doc  = xml.dom.minidom.parse(roll_file)
		nodes = doc.getElementsByTagName('roll')
		for node in nodes:
			name = node.getAttribute('name')
			version = node.getAttribute('version')
			arch = node.getAttribute('arch')
			url = node.getAttribute('url')
			diskid = node.getAttribute('diskid')
			release = node.getAttribute('release')
			rolls.append((name, version, release, arch, url, diskid))

		self.rolls = rolls
