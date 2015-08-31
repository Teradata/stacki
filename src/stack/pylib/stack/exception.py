# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
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
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@

import types
import string

class StackError(Exception):

	def __init__(self, msg):
                self.msg = msg

        def __str__(self):
                return 'error - %s' % self.message()

        def message(self):
                return self.msg
        

class CommandError(StackError):

        def __init__(self, cmd, msg):
                self.cmd = cmd
                super(CommandError, self).__init__(msg)

class UsageError(CommandError):
        
        def __init__(self, cmd, msg):
                super(UsageError, self).__init__(cmd, msg)

        def message(self):
                return '%s\n%s' % (self.msg, self.usage())

        def usage(self):
                return self.cmd.usage()


class ArgParamBaseError(UsageError):
        
        def __init__(self, cmd, arg, msg):
                if type(arg) == types.StringType:
                        args = [ arg ]
                else:
                        args = arg
                        
                list = []
                for a in args:
                        list.append('"%s"' % a)
                args = string.join(list, ' or ')
                                
                m = '%s %s %s' % (args, self.argumentType(), msg)
                super(ArgParamBaseError, self).__init__(cmd, m)

        def argumentType(self):
                return ''
        
class ArgError(ArgParamBaseError):
        
        def __init__(self, cmd, arg, msg):
                super(ArgError, self).__init__(cmd, arg, msg)

        def argumentType(self):
                return 'argument'

                
class ArgRequired(ArgError):

        def __init__(self, cmd, arg):
                super(ArgRequired, self).__init__(cmd, arg, 'is required')

class ArgValue(ArgError):

        def __init__(self, cmd, arg, value):
                super(ArgValue, self).__init__(cmd, arg, 'must be %s' % value)

class ArgUnique(ArgValue):

        def __init__(self, cmd, arg):
                super(ArgUnique, self).__init__(cmd, arg, 'unique')



class ParamError(ArgParamBaseError):
        
        def __init__(self, cmd, param, msg):
                super(ParamError, self).__init__(cmd, param, msg)

        def argumentType(self):
                return 'parameter'
                
class ParamRequired(ParamError):

        def __init__(self, cmd, param):
                super(ParamRequired, self).__init__(cmd, param, 'is required')

class ParamType(ParamError):

        def __init__(self, cmd, param, type):
                if type[0] in [ 'a', 'e', 'i', 'o', 'u' ]:
                        article = 'an'
                else:
                        article = 'a'
                super(ParamType, self).__init__(cmd, param, 'must be %s %s' % (article, type))

class ParamValue(ParamError):

        def __init__(self, cmd, param, value):
                super(ParamValue, self).__init__(cmd, param, 'must be %s' % value)

        
