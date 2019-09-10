# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@


from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()
bootaction = ObjectType("Bootaction")

@query.field("bootnames")
def resolve_bootnames(*_):
    results, _ = db.run_sql("SELECT id, name, type FROM bootnames")
    return results

@query.field("bootname")
def resolve_bootname(_, info, id):
	cmd = """
		SELECT id, name, type 
		FROM bootnames 
		WHERE id=%s
	"""
	args = (id,)
	result,_ = db.run_sql(cmd, args, fetchone=True)
	return result

@mutation.field("addBootname")
def resolve_add_bootname(_, info, name, type):
	# Check for existing bootname type 
	select_cmd = """
		SELECT id, name, type
		FROM bootnames
		WHERE name=%s AND type=%s
	"""
	args = (name, type)
	bootname, _ = db.run_sql(select_cmd, args, fetchone=True)
	if bootname:
		raise Exception("The bootname name and type already exist")

	# Insert bootname
	cmd = """
		INSERT
		INTO bootnames
		(name, type)
		VALUES (%s, %s)
	"""
	args = (name, type)
	db.run_sql(cmd, args)

	# Get the value we just inserted
	result, _ = db.run_sql(select_cmd, args, fetchone=True)
	return result

@mutation.field("updateBootname")
def resolve_update_bootname(obj, info, id, name=None, type=None):
	bootname = resolve_bootname(obj, info, id)
	# Check if bootname exists
	if not bootname:
		raise Exception("No bootname found")	
	else:
		# Check for duplicates
		new_name = name if name else bootname["name"]
		new_type = type if type else bootname["type"]
		select_cmd = """
			SELECT id
			FROM bootnames
			WHERE name=%s AND type=%s
		"""
		args = (name, type)
		_, affected_rows = db.run_sql(select_cmd, args)
		if affected_rows > 0:
			raise Exception("Bootname with new parameters already exists")

	update_params = []
	args = []
	if name:
		update_params.append("name=%s")
		args.append(name)

	if type:
		update_params.append("type=%s")
		args.append(type)

	cmd = f'UPDATE bootnames SET {", ".join(update_params)} WHERE id=%s'		
	args.append(id)
	db.run_sql(cmd, args)

	result = resolve_bootname(obj, info, id)
	return result

@mutation.field("deleteBootname")
def resolve_delete_bootname(_, info, id):
	cmd = """
		DELETE 
		FROM bootnames 
		WHERE ID=%s
	"""
	args = (id,)
	_, affected_rows = db.run_sql(cmd, args)

	if not affected_rows:
		return False

	return True

@bootaction.field("boot_name")
def resolve_bootname_from_parent(parent, info):
	if parent is None or not parent.get("boot_name_id"):
		return None

	cmd = """
		SELECT id, name, type
		FROM bootnames
		WHERE id=%s
	"""
	args = [parent["boot_name_id"]]
	result, _ = db.run_sql(cmd, args, fetchone=True)

	return result

object_types = [bootaction]
