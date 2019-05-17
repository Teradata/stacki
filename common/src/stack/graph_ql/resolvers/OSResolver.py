# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import graphene
from stack.db import db

class Os(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()

class Query:
	all_oses = graphene.List(Os)

	def resolve_all_oses(self, info):
		db.execute("""
		select id, name from oses
		""")

		return [Os(**os) for os in db.fetchall()]