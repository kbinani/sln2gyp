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
