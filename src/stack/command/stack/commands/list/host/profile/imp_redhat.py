#
# @SI_Copyright@
#                               stacki.com
#                                  v3.2
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

        def output(self, text, tag=False):
                if tag:
                        self.owner.addOutput(self.host, self.owner.annotate(text))
                else:
                        self.owner.addOutput(self.host, text)

	def run(self, args):

		host      = args[0]
		xml       = args[1]
                section   = args[2]
                self.host = host

                if section in [ 'all' ]:
			sections = [
				'main',
				'packages',
				'pre',
				'post',
				'boot',
				'installclass'
				]
                else:
                        sections = [ section ]

		generator = stack.gen.Generator_redhat()
		if xml == None:
			xml = self.owner.command('list.host.xml', [ host, 'os=redhat' ])
		generator.parse(xml)

		self.output('<profile os="redhat">', True)
		self.output('<chapter name="order">', True)
		self.output('<![CDATA[')
                for line in generator.generate('order'):
                        self.output(line)
		self.output(']]>')
		self.output('</chapter>', True)
		self.output('<chapter name="debug">', True)
		self.output('<![CDATA[')
                for line in generator.generate('debug'):
                        self.output(line)
		self.output(']]>')
		self.output('</debug>', True)
		self.output('<chapter name="kickstart">', True)
		self.output('<![CDATA[')
                for section in sections:
                        for line in generator.generate(section, annotation=self.owner.annotation):
                                self.output(line)
		self.output(self.owner.annotate(']]>'))
		self.output(self.owner.annotate('</chapter>'))
		self.output(self.owner.annotate('</profile>'))
