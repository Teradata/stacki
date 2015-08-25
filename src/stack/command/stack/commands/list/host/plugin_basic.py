# @SI_Copyright@
# @SI_Copyright@

import stack.commands

class Plugin(stack.commands.Plugin):

        def provides(self):
                return 'basic'

        def run(self, hosts):

                dict = { }
                for host in hosts:
                        dict[host] = True
                        
                for row in self.db.select("""
	                n.name, n.rack, n.rank, n.cpus, a.name, d.name,
			n.runaction, n.installaction from
			nodes n, appliances a, distributions d where 
			n.appliance=a.id and n.distribution=d.id
			"""):
                        if dict.has_key(row[0]):
                                dict[row[0]] = row[1:]
        
                return { 'keys' : [ 'rack',
                                    'rank',
                                    'cpus',
                                    'appliance',
                                    'distribution',
                                    'runaction',
                                    'installaction' ],
                        'values': dict }

                
