import re
import os.path
from project import Project
import util
from configuration import Configuration

class Solution:
	class Parser:
		class Status:
			kUnknown = 0
			kConfigurationPlatforms = 1

		class Stack:
			def __init__(self):
				self._storage = []

			def push(self, o):
				self._storage.append(o)

			def pop(self):
				return self._storage.pop()

			def peek(self):
				size = len(self._storage)
				if size > 0:
					return self._storage[size - 1]
				else:
					return None

		def __init__(self, solution):
			self._solution = solution
			self._re_project = re.compile('^\s*Project\s*\(\s*"(?P<classid>[^"]*)"\s*\)\s*=\s*"(?P<project_name>[^"]*)"\s*,\s*"(?P<project_file>[^"]*)"\s*,\s*"(?P<project_classid>[^"]*)"\s*(#.*)?$')
			self._re_endproject = re.compile('^\s*EndProject\s*(#.*)?$')
			self._re_globalsection = re.compile('^\s*GlobalSection\s*\(\s*(?P<section_name>[^)]*)\s*\)\s*=\s*[^#]*(#.*)?$')
			self._re_endglobalsection = re.compile('^\s*EndGlobalSection\s*(#.*)?$')

			self._project = None
			self._status = Solution.Parser.Stack()

		def parse(self, file):
			self._solution._file = util.normpath(os.path.abspath(file))
			for line in open(file, 'r'):
				self._append(line)

		def _append(self, line):
			m = self._re_project.search(line)
			if not m == None:
				file = util.normpath(self._solution.solution_dir() + '/' + m.group('project_file'))
				classid = m.group('project_classid')
				name = m.group('project_name')
				self._project = Project(file, name, classid)
				return

			m = self._re_endproject.search(line)
			if not m == None:
				self._solution._projects.append(self._project)
				self._project = None
				return

			m = self._re_globalsection.search(line)
			if not m == None:
				section_name = m.group('section_name')
				if section_name == 'SolutionConfigurationPlatforms':
					self._status.push(Solution.Parser.Status.kConfigurationPlatforms)
				else:
					self._status.push(Solution.Parser.Status.kUnknown)
				return

			m = self._re_endglobalsection.search(line)
			if not m == None:
				self._status.pop()
				return

			if self._status.peek() == Solution.Parser.Status.kConfigurationPlatforms:
				rhs, lhs = line.split('=')
				configuration = Configuration.create_from_string(lhs.strip())
				self._solution._configurations.append(configuration)

	def __init__(self, file):
		self._projects = []
		self._file = file
		self._configurations = []
		parser = Solution.Parser(self)
		parser.parse(file)

	def solution_dir(self):
		return os.path.dirname(self._file)

	def solution_file(self):
		return self._file

	def projects(self):
		return self._projects

	def get_by_guid(self, guid):
		for p in self._projects:
			if guid == p.guid():
				return p
		return None

	def configurations(self):
		return self._configurations
