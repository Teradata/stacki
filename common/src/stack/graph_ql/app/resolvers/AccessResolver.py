# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from ariadne import ObjectType, QueryType, MutationType
import app.db as db

query = QueryType()
mutation = MutationType()

@query.field("access")
def resolve_access(*_):

	# The resolver diverges from the original stacki command in that it
	# only takes in and returns group id's vs the group names as well.
	# This is due to the original command depending on the unix groups
	# present on the frontend which we can't guarantee are in the db
	# container as well.
	results, _ = db.run_sql("SELECT groupId, command FROM access")
	return results

@mutation.field("addAccess")
def resolve_add_access(_, info, groupId, command):

	# TODO: Add a primary key to access table
	if groupId in [grp_access['groupId'] for grp_access in resolve_access()]:
		raise Exception(f'User Group ID {groupId} already exists')

	# Add a new group id with the commands it can use
	cmd = 'INSERT INTO access (groupId, command) VALUES(%s, %s)'
	args = (groupId, command)
	results, _ = db.run_sql(cmd, args)

	# Get the recently inserted value
	cmd = "SELECT groupId, command FROM access WHERE groupId=%s"
	args = (groupId, )
	results, _ = db.run_sql(cmd, args, fetchone=True)
	return results

@mutation.field("deleteAccess")
def resolve_delete_access(_, info, groupId):
	cmd = "DELETE FROM access WHERE groupId=%s"
	args = (groupId,)
	_, affected_rows = db.run_sql(cmd, args)

	# Return false if the db can't find the row to delete
	if not affected_rows:
		return False

	return True

object_types = []
