# @SI_Copyright@
# @SI_Copyright@

import types
import string

class CommandError(Exception):

        def __init__(self, msg):
                self.msg = msg

        def __str__(self):
                return 'error - %s' % self.message()

        def message(self):
                return self.msg


class UsageError(CommandError):
        
        def __init__(self, cmd, msg):
                self.cmd = cmd
                super(UsageError, self).__init__(msg)

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
                super(ParamInteger, self).__init__(cmd, param, 'must be %s %s' % (article, type))

class ParamValue(ParamError):

        def __init__(self, cmd, param, value):
                super(ParamInteger, self).__init__(cmd, param, 'must be %s' % value)

        
