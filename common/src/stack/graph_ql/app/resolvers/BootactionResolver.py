# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()

@query.field("bootactions")
def resolve_bootactions(parent, info, os_name=None, boot_name=None, **kwargs):
	where_conditionals = {
		f"bootactions.{key}": value
		for key, value in kwargs.items()
		if key in ("id", "boot_name_id", "os_id", "kernel", "ramdisk", "args")
	}
	ignored_kwargs = set(key.split(".")[-1] for key in where_conditionals.keys()).difference(set(kwargs))
	if ignored_kwargs:
		raise ValueError(f"Received unsupported kwargs {ignored_kwargs}")

	cmd = """
		SELECT
			bootactions.ID as id,
			bootactions.BootName as boot_name_id,
			bootactions.OS as os_id,
			bootactions.Kernel as kernel,
			bootactions.Ramdisk ramdisk,
			bootactions.Args as args
		FROM bootactions
		{join}
		{where}
	"""
	join_string = ""
	if os_name:
		join_string = "INNER JOIN oses ON bootactions.OS=oses.ID "
		where_conditionals["oses.Name"] = os_name

	if boot_name:
		join_string += "INNER JOIN bootnames on bootactions.BootName=bootnames.ID"
		where_conditionals[f"bootnames.Name"] = boot_name

	where_string = "WHERE"
	args = []
	first = True
	for key, value in where_conditionals.items():
		where_string += f" {'' if first else 'and '}{key}=%s"
		args.append(value)
		first = False

	if not args:
		where_string = ""

	cmd = cmd.format(join=join_string, where=where_string)
	result, _ = db.run_sql(cmd, args)

	return result


object_types = []
