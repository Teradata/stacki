# @SI_Copyright@
# @SI_Copyright@

import stack.commands.set.network

class Command(stack.commands.set.network.command):
	"""
        Enables or Disables PXE for one of more networks.

        All hosts must be connected to atleast one network that has
        PXE enabled.

        <arg type='string' name='network' optional='1' repeat='1'> 
        The names of zero of more networks. If no network is specified
        the PXE is set for all existing networks.
	</arg>
	
	<param type='boolean' name='pxe' optional='0'>
        Set to True to enable PXE for the given networks.
	</param>
	
	<example cmd='set network pxe private pxe=true'>
        Enables PXE on the "private" network.
	</example>
	"""
                
        def run(self, params, args):

                (networks, pxe) = self.fillSetNetworkParams(args, 'pxe')
		pxe = self.str2bool(pxe)
                 
        	for network in networks:
			self.db.execute("""
                        	update subnets set pxe=%s where
				subnets.name='%s'
                                """ % (pxe, network))

