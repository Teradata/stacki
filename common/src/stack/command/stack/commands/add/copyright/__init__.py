# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import os
import tempfile
import shutil
import stack.file
import stack.commands


class Command(stack.commands.add.command):
        """
        Insert a copyright for each file under a directory.

        This a used exclusively by stacki developers to ensure all files
        have current copyright statements.

	<arg/>
        """

        def iter(self, dir, file, root):

                try:
                        dirs = file.getFullName().split('/')
                except:
                        dirs = [ ]

                # Don't process non-source code.

                for skip in [ '.git', 'build-' ]:
                        if skip in dirs:
                                return
                        for d in dirs:
                                if d.find(skip) == 0:
                                        return

                try:
                        fin = open(file.getFullName(), 'r')
                except IOError:
                        return

                tmp = tempfile.mktemp()
                fout = open(tmp, 'w')
                
                state  = 0      # 0 - outside block, 1 - inside block
                blocks = 0      # number of copyright blocks found
                try:
                        lines = fin.readlines()
                except:
                        lines = []
                for line in lines:
                        pos = line.find(self.pattern[state])
                        if pos >= 0:
                                state = state ^ 1
                                if not state:
                                        blocks += 1
                                else:
                                        prefix = line[0:pos]
                                        suffix = line[pos + len(self.pattern[0]):]
                                        fout.write(line)
                                        for text in self.copyright:
                                                fout.write('%s%s%s' % (
                                                        prefix,
                                                        text,
                                                        suffix))
                        if not state:
                                fout.write(line)
                        
                fin.close()
                fout.close()
                
                # Commit the replaced text only if a complete copyright
                # block was found.  This will make sure a single copyright
                # tag in a file does not cause all the code to be lost.
                
                if blocks:
                        print(file.getFullName())
                        shutil.copymode(file.getFullName(), tmp)
                        try:
                                shutil.copyfile(tmp, file.getFullName())
                        except IOError as msg:
                                pass
                os.unlink(tmp)
                                

        def run(self, params, args):
                
                path = os.path.dirname(__file__)
                copyright = {}
                copyright['stacki-long']  = os.path.join(path, 'copyright-stacki-short')
                copyright['stacki-short'] = os.path.join(path, 'copyright-stacki-short')
                copyright['rocks-long']   = os.path.join(path, 'copyright-rocks-short')
                copyright['rocks-short']  = os.path.join(path, 'copyright-rocks-short')

                for (k, v) in copyright.items():
                        file = open(v, 'r')
                        copyright[k] = []
                        print(file)
                        for line in file.readlines():
                                copyright[k].append(line[:-1])

                # We breakup the string below to protect this code segment
                # for insert-copyright detecting the tags.  Otherwise we
                # could not run on ourselves.
                self.tree = stack.file.Tree('../../../../..')
                
                print('Inserting stacki copyright into source code files...')
                self.pattern   = [ '@' + 'copyright@', '@' + 'copyright@' ]
                self.copyright = copyright['stacki-long']
                self.tree.apply(self.iter)

                print('Inserting stacki copyright into XML files...')
                self.pattern = [ '<' + 'copyright>', '<' + '/copyright>' ]
                self.copyright = copyright['stacki-short']
                self.tree.apply(self.iter)

                self.pattern = [ '<' + 'stack:copyright>', '<' + '/stack:copyright>' ]
                self.tree.apply(self.iter)


                # No reason to keep updating the Rocks stuff, we forked years
                # ago and never looked back.
                #
                # Keep the code here if for when/if the trees ever come back
                # together.

                print('Inserting rocks copyright into source code files...')
                self.pattern   = [ '@' + 'rocks@', '@' + 'rocks@' ]
                self.copyright = copyright['rocks-long']
                self.tree.apply(self.iter)
                
                print('Inserting rocks copyright into XML files...')
                self.pattern = [ '<' + 'rocks>', '<' + '/rocks>' ]
                self.copyright = copyright['rocks-short']
                self.tree.apply(self.iter)

                self.pattern = [ '<' + 'stack:rocks>', '<' + '/stack:rocks>' ]
                self.tree.apply(self.iter)

