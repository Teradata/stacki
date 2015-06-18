# @SI_Copyright@
# @SI_Copyright@

import stack.commands

class Command(stack.commands.set.host.interface.command):
	"""
        Designates one network as the default route for a set of hosts.
        Either the interface or network paramater is required.

	<arg optional='1' repeat='1' type='string' name='host'>
	Host name.
	</arg>
	
	<param optional='0' type='string' name='interface'>
	Device name of the default interface.
 	</param>

        <param optional='0' type='string' name='network'>
 	Network name of the default interface.
 	</param>

        <param optional='0' type='bool' name='default'>
        Can be used to set the value of default to False.
        This is used to remove all default networks.
        </param>

	"""

	def run(self, params, args):

                (interface, network, default) = self.fillParams([
                        ('interface', None),
                        ('network', None),
                        ('default', 'True')])

                default = self.str2bool(default)

		if not interface and not network:
                        self.abort('must specify a network or interface name')

                for host in self.getHostnames(args):
                        if network:
                                interface = self.getInterface(host, network)
                        if not interface:
                                self.abort('no interface for "%s" on "%s"' %
                                	(network, host))

                        if not self.verifyInterface(host, interface):
                                self.abort('no interface "%s" on "%s"' %
                                        (interface, host))

                        # Exclusively set the default interface by resetting
                        # all other interfaces after enabling the specified one.
                        
                        self.db.execute("""
                        	update networks net, nodes n
                                set net.main = %s
                                where
                                n.name = '%s' and net.node = n.id and
                                net.device = '%s'
                                """ % (default, host, interface))
                        if default:
                                self.db.execute("""
                        		update networks net, nodes n
                                	set net.main='False'
                                	where
                                	n.name='%s' and net.node=n.id and
                                	net.device != '%s'
                                	""" % (host, interface))
                        

