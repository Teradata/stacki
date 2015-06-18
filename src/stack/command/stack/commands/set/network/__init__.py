# @SI_Copyright@
# @SI_Copyright@

import stack.commands

class command(stack.commands.set.command,
              stack.commands.NetworkArgumentProcessor):

        def fillSetNetworkParams(self, args, paramName):

                networks = self.getNetworkNames(args)
                if not networks:
                        self.abort('network "%s" not defined' % args)

                (param, ) = self.fillParams([(paramName, None)])
                if not param:
                        self.abort('%s not specified' % paramName)

                return (networks, param)


