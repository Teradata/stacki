# @copyright@
# @copyright@

from collections import OrderedDict
from stack.exception import StackError
from stack.api.base  import Base
import stack.api

class Component(Base):

	def __init__(self):
		self.appliance   = stack.api.Appliance()
		self.environment = stack.api.Environment()

	def get_names(self):
		result = [ ]
		for name, in self.db.select('name from components'):
			result.append(name)
		return result

	def add(self, component, appliance, rack, rank):

		component = component.lower()

		if component in self.get_names():
			raise StackError('component "%s" exists' % component)


		# If the name is over the form appliance-rack-rank then
		# use the name to figure out the values of these
		# parameters.
		if appliance is None and rack is None and rank is None:
			try:
				appliance, rack, rank = component.split('-')
			except:
				pass


		if not appliance or appliance not in self.appliance.get_names():
			raise StackError('invalid appliance "%s"' % appliance)

		if rack is None:
			raise StackError('invalid rack "%s"' % rack)

		if rank is None:
			raise StackError('invalid rank "%s"' % rank)

		self.db.execute("""
			insert into components 
			(name, appliance, rack, rank)
			values (%s, 
				(select id from appliances where name=%s),
				%s, %s)
			""", (component, appliance, rack, rank))


	def set(self, component, **kwargs):
		self.set_multiple((component, ), **kwargs)

	def set_multiple(self, components, *, 
			 name=None, appliance=None, rack=None, rank=None, make=None, model=None, 
			 environment=None, comment=None):

		everyone = self.get_names()
		for component in components:
			if component not in everyone:
				raise StackError('invalid component "%s"' % component)

		fields = [ ]
		values = [ ]
		if name:
			fields.append('name=%s')
			values.append(name)
		if appliance:
			if appliance not in self.appliance.get_names():
				raise StackError('invalid appliance "%s"' % appliance)
			fields.append('appliance=(select id from appliances where name=%s)')
			values.append(appliance)
		if rack:
			fields.append('rack=%s')
			values.append(rack)
		if rank:
			fields.append('rank=%s')
			values.append(rank)
		if make:
			fields.append('make=%s')
			values.append(make)
		if model:
			fields.append('model=%s')
			values.append(model)
		if environment:
			if environment not in self.environment.get_names():
				raise StackError('invalid environment "%s"' % environment)
			fields.append('environment=(select id from environments where name=%s)')
			values.append(environment)
		if comment:
			if len('%s' % comment) > 132:
				raise StackError('comment "%s" is too long' % comment)
			fields.append('comment=%s')
			values.append(comment)
		if not values:
			return

		for component in components:
			sql = [ 'update components set' ]
			sql.append(','.join(fields))
			sql.append('where name=%s')
			values.append(component)

			self.db.execute(' '.join(sql), values)


	def list(self, component):
		return self.list_multiple((component, ))

	def list_multiple(self, components):

		if not components:
			return {}

		result = OrderedDict.fromkeys(components)
		for row in self.db.select(
			"""
			c.name, c.rack, c.rank, c.make, c.model,
			a.name, e.name,
			c.comment from
			components c
			left join appliances a   on c.appliance   = a.id
			left join environments e on c.environment = e.id 
			"""):
			if row[0] in result:
				result[row[0]] = OrderedDict({ 'component'   : row[0],
							       'rack'        : row[1],
							       'rank'        : row[2],
							       'make'        : row[3],
							       'model'       : row[4],
							       'appliance'   : row[5],
							       'environment' : row[6],
							       'comment'     : row[7] })
		return result







