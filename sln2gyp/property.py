from copy import copy

class Property:
	def __init__(self, default_value):
		self._storage = {}
		self._default = default_value

	def set(self, configuration, value):
		name = configuration.configuration()
		platform = configuration.platform()
		if not (name in self._storage):
			self._storage[name] = {}
		self._storage[name][platform] = value

	def get(self, configuration):
		name = configuration.configuration()
		platform = configuration.platform()
		if name in self._storage:
			if platform in self._storage[name]:
				return self._storage[name][platform]
		return copy(self._default)

	def set_default(self, default_value):
		self._default = default_value

	def get_default(self):
		return self._default

	def get_common_value_for_configurations(self, configurations, key = None):
		is_first = True
		value = None
		for config in configurations:
			v = None
			if key == None:
				v = self.get(config)
			else:
				if key in self.get(config):
					v = self.get(config)[key]

			if is_first:
				value = v
				is_first = False
			else:
				if v != value:
					return None
		return value
