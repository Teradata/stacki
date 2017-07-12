# @SI_Copyright@
#                               stacki.com
#                                  v4.0
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
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

import os
import sys
import csv
import re
from io import StringIO
import stack.commands
import stack.attr

class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
	This command outputs all the attributes
	of a system in a CSV format.

	<param name="filter" type="string" optional="1">
	Filter out only the attributes that you want.
	</param>
	"""

	def run(self, params, args):

		(attr_filter, ) = self.fillParams([ ("filter", None), ])

		header		= []
		csv_attrs	= []
		regex		= None

		if attr_filter:
			regex = re.compile(attr_filter)


		for scope in [ 'global', 'os', 'appliance', 'environment', 'host' ]:
			for row in self.call('list.attr', [ 'scope=%s' % scope, 'resolve=false', 'const=false', 'shadow=false' ]):
				if scope == 'global':
					target = 'global'
				else:
					target = row[scope]
				attr   = row['attr']
				value  = row['value']

				if regex and regex.match(attr):
					continue

				csv_attrs.append({'target': target, attr: value})
				if attr not in header:
					header.append(attr)

		header.sort()
		header.insert(0, 'target')

		s = StringIO()
		w = csv.DictWriter(s, header)
		w.writerows(csv_attrs)

		self.beginOutput()
		self.addOutput(None, s.getvalue())
		self.endOutput(trimOwner=True)
