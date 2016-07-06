# @SI_Copyright@
#                             www.stacki.com
#                                  v3.1
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

import pytest
import random
import stack
from stack.bool import *
from stack.api import *

def test_box():
	"""
	Test list/add/remove/set box.
	"""

	# Search for a unused box name and use it for
	# the following tests.

	done = False
	while not done:
		box = 'default-%s' % str(random.randint(0, 100))
		result = Call('list box', [ box ])
		if ReturnCode() and not result:
			done = True
	assert box

	# add box

	result = Call('add box', [ box ])
	assert ReturnCode() == 0 and result == []

	# lookup current box for host

	result = Call('list host', [ 'localhost' ])
	assert ReturnCode() == 0 and len(result) == 1
	prevBox = result[0]['box']

        # set box for this host

        result = Call('set host box', [ 'localhost', 'box=%s' % box ])
        assert ReturnCode() == 0

	# verify box was set

	result = Call('list host', [ 'localhost' ])
	assert ReturnCode() == 0 and len(result) == 1
	assert result[0]['box'] == box

	# restore prev setting

	result = Call('set host box', [ 'localhost', 'box=%s' % prevBox ])
	assert ReturnCode() == 0

        # remove box

        result = Call('remove box', [ box ])
        assert ReturnCode() == 0

	# try to remove default
	#	"remove box" should protect against this

       	result = Call('remove box', [ 'default' ])
	assert ReturnCode() == 255

