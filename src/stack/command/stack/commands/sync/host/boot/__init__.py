# @SI_Copyright@
# @SI_Copyright@

import subprocess
import stack.commands

class Command(stack.commands.sync.host.command):

	def run(self, params, args):

                p = subprocess.Popen(['/opt/stack/bin/stack','report','script'],
                                     stdin  = subprocess.PIPE,
                                     stdout = subprocess.PIPE,
                                     stderr = subprocess.PIPE)

                for row in self.call('report.host.bootfile', 
                                     self.getHostnames(args, managed_only=True)):
                        p.stdin.write('%s\n' % row['col-1'])
                o, e = p.communicate('')

                psh = subprocess.Popen(['/bin/sh'],
                                       stdin  = subprocess.PIPE,
                                       stdout = subprocess.PIPE,
                                       stderr = subprocess.PIPE)
                out, err = psh.communicate(o)
    
