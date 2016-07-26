#
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
#

import stack.commands
import stack.gen

class Implementation(stack.commands.Implementation):
	def run(self, args):

		host = args[0]
		xml = args[1]

		c_gen = getattr(stack.gen,'Generator_%s' % self.owner.os)
		self.generator = c_gen()
		self.generator.setArch(self.owner.arch)
		self.generator.setOS(self.owner.os)

		if xml == None:
			xml = self.owner.command('list.host.xml', 
			[
			 host,
			 'os=%s' % self.owner.os,
			])
		self.runXML(xml, host)

	def runXML(self, xml, host):
		"""Reads the XML host profile and outputs a RedHat 
		Kickstart file."""

		list = []
		self.generator.parse(xml)
		if self.owner.section == 'all':
			for section in [
				'order',
				'debug',
				'main',
				'packages',
				'pre',
				'post',
				'boot',
				'installclass'
				]:
				list += self.generator.generate(section,
					annotation=self.owner.annotation)
		else:
			list += self.generator.generate(self.owner.section,
					annotation=self.owner.annotation)
		self.owner.addOutput(host,
			self.owner.annotate('<profile lang="kickstart">'))
		self.owner.addOutput(host,
			self.owner.annotate('<section name="kickstart">'))
		self.owner.addOutput(host, self.owner.annotate('<![CDATA['))
		for i in list:
			self.owner.addOutput(host, i)
		self.owner.addOutput(host, self.owner.annotate(']]>'))
		self.owner.addOutput(host, self.owner.annotate('</section>'))
		self.owner.addOutput(host, self.owner.annotate('</profile>'))
