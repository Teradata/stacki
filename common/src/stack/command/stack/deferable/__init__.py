# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from functools import wraps
import stack.repo

def rewrite_frontend_repo_file(command_run_method):
	@wraps(command_run_method)
	def wrapper(*args, **kwargs):
		command_obj = args[0]
		original_box_data = command_obj.call('list.box', [command_obj.db.getHostBox('localhost')])
		command_run_method(*args, **kwargs)
		new_box_data = command_obj.call('list.box', [command_obj.db.getHostBox('localhost')])
		if original_box_data != new_box_data:
			command_obj.deferred.callback(stack.repo.rewrite_repofile)
	return wrapper
