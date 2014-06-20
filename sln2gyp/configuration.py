class Configuration:
	def __init__(self, configuration, platform):
		self._configuration = configuration
		self._platform = platform

	def configuration(self):
		return self._configuration

	def platform(self):
		return self._platform

	def is_match(self, condition):
		condition = condition.replace(' ', '')
		condition = condition.replace('$(Configuration)', self._configuration)
		condition = condition.replace('$(Platform)', self._platform)
		return eval(condition)

	@staticmethod
	def create_from_string(str):
		configuration, platform = str.split('|')
		return Configuration(configuration, platform)

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
		return self._default

	def set_default(self, default_value):
		self._default = default_value

	def get_common_value_for_configurations(self, configurations, getter = None):
		value = None
		for config in configurations:
			v = None
			if getter == None:
				v = self.get(config)
			else:
				v = getter(self.get(config))

			if value == None:
				value = v
			else:
				if v != value:
					return None
		return value