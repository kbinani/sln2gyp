class Level:
	Debug = 0,
	Info = 1,
	Warning = 2,
	Error = 3,

class Log:
	def __init__(self):
		self.__header = '[sln2gyp]'
		self.__level = Level.Info
		self.__kind = {
			Level.Debug: '[debug]',
			Level.Info: '[info]',
			Level.Warning: '[warn]',
			Level.Error: '[error]',
		}

	def write(self, message, level):
		if level >= self.__level:
			print self.__header + self.__kind[level] + ' ' + message

	def set_level(self, level):
		self.__level = level

__log = Log()

def info(message):
	__log.write(message, Level.Info)

def warn(message):
	__log.write(message, Level.Warning)

def debug(message):
	__log.write(message, Level.Debug)

def error(message):
	__log.write(message, Level.Error)

def set_level(level):
	__log.set_level(level)
