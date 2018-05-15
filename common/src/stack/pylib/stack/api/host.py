# @copyright@
# @copyright@

try:
	import redis
except:
	pass
from collections import OrderedDict
from stack.exception import CommandError, ParamRequired, ArgUnique
from stack.api.base  import Base
import stack.api

class Host(Base):

	def __init__(self):
		self.component  = stack.api.Component()
		self.box        = stack.api.Box()
		self.bootaction = stack.api.BootAction()

	def get_names(self):
		result = [ ]
		for name, in self.db.select('name from host_view'):
			result.append(name)
		return result

	def add(self, host, appliance, rack, rank):

		self.component.add(host, appliance, rack, rank)

		# Connect the host information to the components table, the
		# LAST_INSERT_ID() is magic, but it really is safe.

		self.db.execute('insert into hosts (hostid) values (NULL)')
		self.db.execute("""
			update components set
			host=last_insert_id() where
			name=%s
			""", (host, ))


	def set(self, host, **kwargs):
		self.set_multiple((host, ), **kwargs)
	
	def set_multiple(self, hosts, *, 
			 box=None, osaction=None, installaction=None):

		everyone = self.get_names()
		for host in hosts:
			if host not in everyone:
				raise StackError('invalid host "%s"' % host)

		fields = [ ]
		values = [ ]
		if box:
			if box not in self.box.get_names():
				raise StackError('invalid box "%s"' % box)
			fields.append("box=(select id from boxes where name=%s)")
			values.append(box)
		if osaction:
			if osaction not in self.bootaction.get_names('os'):
				raise StackError('invalid osaction "%s"' % osaction)
			fields.append("osaction=(select id from bootnames where name=%s and type='os')")
			values.append(osaction)
		if installaction:
			if installaction not in self.bootaction.get_names('install'):
				raise StackError('invalid installaction "%s"' % installaction)
			fields.append("installaction=(select id from bootnames where name=%s and type='install')")
			values.append(installaction)
		if not values:
			return
		
		for host in hosts:
			sql = [ 'update host_view set' ]
			sql.append(','.join(fields))
			sql.append("where name=%s")
			values.append(host)

			self.db.execute(' '.join(sql), values)



	def list(self, host):
		return self.list_multiple((host, ))

	def list_multiple(self, hosts):

		if not hosts:
			return {}

		result = OrderedDict.fromkeys(hosts)

		for row in self.db.select(
			"""
			hv.name, hv.rack, hv.rank, hv.make, hv.model, hv.comment,
			a.name,
			o.name, b.name, 
			e.name, 
			bno.name, bni.name from 
			host_view hv
			left join appliances a   on hv.appliance     = a.id
			left join boxes b        on hv.box           = b.id 
			left join environments e on hv.environment   = e.id 
			left join bootnames bno  on hv.osaction      = bno.id 
			left join bootnames bni  on hv.installaction = bni.id
			left join oses o	 on b.os = o.id
			"""):

			if row[0] in result:
				result[row[0]] = OrderedDict({ 'host'          : row[0],
							       'rack'          : row[1],
							       'rank'          : row[2],
							       'make'          : row[3],
							       'model'         : row[4],
							       'comment'       : row[5],
							       'appliance'     : row[6],
							       'os'            : row[7],
							       'box'           : row[8],
							       'environment'   : row[9],
							       'osaction'      : row[10],
							       'installaction' : row[11]})


		# Mix in the status from redis and move the comment to the end
		# of the dictionary.

		for frontend in [ 'localhost' ]:
			try:
				r = redis.StrictRedis(host=frontend)
				break
			except:
				pass
		for host in hosts:
			try:
				status = r.get('host:%s:status' % host) 
			except:
				status = None
			if status:
				status = status.decode()
			result[host]['status'] = status
			result[host].move_to_end('comment')

		return result




