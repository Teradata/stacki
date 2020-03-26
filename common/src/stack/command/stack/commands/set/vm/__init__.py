# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
from stack.argument_processors.host import HostArgProcessor
from stack.argument_processors.vm import VmArgProcessor

class command(
	HostArgProcessor,
	stack.commands.set.command,
	VmArgProcessor
):
	pass
