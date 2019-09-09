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
	results, _ = db.run_sql("SELECT groupID, command FROM access")
	return results

@mutation.field("addAccess")
def resolve_add_access(_, info, groupID, command):

	# TODO: Add a primary key to access table
	if groupID in [grp_access['groupID'] for grp_access in resolve_access()]:
		raise Exception(f'User Group ID {groupID} already exists')

	# Add a new group id with the commands it can use
	cmd = 'INSERT INTO access (groupID, command) VALUES(%s, %s)'
	args = (groupID, command)
	results, _ = db.run_sql(cmd, args)

	# Get the recently inserted value
	cmd = "SELECT groupID, command FROM access WHERE groupID=%s"
	args = (groupID, )
	results, _ = db.run_sql(cmd, args, fetchone=True)
	return results

@mutation.field("deleteAccess")
def resolve_delete_access(_, info, groupID):
	cmd = "DELETE FROM access WHERE groupID=%s"
	args = (groupID,)
	_, affected_rows = db.run_sql(cmd, args)

	# Return false if the db can't find the row to delete
	if not affected_rows:
		return False

	return True

object_types = []
