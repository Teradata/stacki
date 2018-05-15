# @copyright@
# @copyright@

from stack.api.base import Base

class Appliance(Base):

	def get_names(self):
		result = [ ]
		for name, in self.db.select('name from appliances'):
			result.append(name)
		return result





