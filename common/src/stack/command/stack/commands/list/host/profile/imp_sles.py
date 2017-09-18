#! /opt/stack/bin/python
#
# @copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v5.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.gen
import stack.sles.gen


class Implementation(stack.commands.list.host.profile.implementation):
	
	def generator(self):
		return stack.sles.gen.Generator()



