#
# @SI_COPYRIGHT@
# @SI_COPYRIGHT@        
#               
			
import os       
import stack.commands
			

class Implementation(stack.commands.Implementation):

	def run(self, args):

		cart = args[0]
		cartpath = args[1]

		#
		# write the graph file
		#
		graph = open(os.path.join(cartpath, 'graph',
			'cart-%s.xml' % cart), 'w')
		graph.write("""<?xml version="1.0" standalone="no"?>
<graph>

	<description>
	%s cart
	</description>

	<order head="backend" tail="cart-%s-backend"/>
	<edge  from="backend"   to="cart-%s-backend"/>

</graph>
""" % (cart, cart, cart))

		graph.close()

		#
		# write the node file
		#
		node = open(os.path.join(cartpath, 'nodes',
			'cart-%s-backend.xml' % cart), 'w')
		node.write("""<?xml version="1.0" standalone="no"?>
<kickstart>

<description>
%s cart backend appliance extensions
</description>

<!-- <package></package> -->

<!-- shell code for post RPM installation -->
<post>

</post>
</kickstart>
""" % cart)
		node.close()
		
