import re
import os.path
from project import Project
import util
from configuration import Configuration

class Solution:
	class Parser:
		class StatusType:
			kUnknown = 0
			kGlobalSection = 1
			kProject = 2
			kProjectSection = 3
			kRoot = 4

		class Status:
			def __init__(self, status_type, name = None):
				self._status_type = status_type
				self._name = name

			def status_type(self):
				return self._status_type

			def name(self):
				return self._name

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
			self._re_projectsection = re.compile('^\s*ProjectSection\((?P<section_name>[^)]*)\)\s*=\s*[^#]*(#.*)?$')
			self._re_endprojectsection = re.compile('^\s*EndProjectSection\s*(#.*)?$')

			self._project = None
			self._status = Solution.Parser.Stack()
			self._status.push(Solution.Parser.Status(Solution.Parser.StatusType.kRoot))

		def parse(self, file):
			self._solution._file = util.normpath(os.path.abspath(file))
			for line in open(file, 'r'):
				self._append(line)

		def _append(self, line):
			m = self._re_project.search(line)
			if not m == None:
				file = util.normpath(self._solution.solution_dir + '/' + m.group('project_file'))
				classid = m.group('classid')
				guid = m.group('project_classid')
				name = m.group('project_name')
				self._project = Project(file, name, guid)
				status = Solution.Parser.Status(Solution.Parser.StatusType.kProject, classid)
				self._status.push(status)
				return

			m = self._re_endproject.search(line)
			if not m == None:
				self._solution._projects.append(self._project)
				self._project = None
				if self._status.peek().status_type() != Solution.Parser.StatusType.kProject:
					raise "Invalid .sln format"
				self._status.pop()
				return

			m = self._re_globalsection.search(line)
			if not m == None:
				section_name = m.group('section_name')
				status = Solution.Parser.Status(Solution.Parser.StatusType.kGlobalSection, section_name)
				self._status.push(status)
				return

			m = self._re_endglobalsection.search(line)
			if not m == None:
				if self._status.peek().status_type() != Solution.Parser.StatusType.kGlobalSection:
					raise "Invalid .sln format"
				self._status.pop()
				return

			m = self._re_projectsection.search(line)
			if m != None:
				section_name = m.group('section_name')
				status = Solution.Parser.Status(Solution.Parser.StatusType.kProjectSection, section_name)
				self._status.push(status)
				return

			m = self._re_endprojectsection.search(line)
			if m != None:
				if self._status.peek().status_type() != Solution.Parser.StatusType.kProjectSection:
					raise "Invalid .sln format"
				self._status.pop()
				return

			current_status = self._status.peek()
			if current_status == None:
				#TODO: error handling. self._status hould have 'root' status
				return

			if current_status.status_type() == Solution.Parser.StatusType.kGlobalSection:
				if current_status.name() == 'SolutionConfigurationPlatforms':
					rhs, lhs = line.split('=')
					configuration = Configuration.create_from_string(lhs.strip())
					self._solution._configurations.append(configuration)
			elif current_status.status_type() == Solution.Parser.StatusType.kProjectSection:
				if current_status.name() == 'ProjectDependencies':
					rhs, lhs = line.split('=')
					guid = self._project.guid
					depends = lhs.strip()
					self._project._dependencies.append(depends)

	def __init__(self, file):
		self._projects = []
		self._file = file
		self._configurations = []
		parser = Solution.Parser(self)
		parser.parse(file)

	@property
	def solution_dir(self):
		return os.path.dirname(self._file)

	@property
	def solution_file(self):
		return self._file

	@property
	def projects(self):
		return self._projects

	def get_by_guid(self, guid):
		for p in self._projects:
			if guid == p.guid:
				return p
		return None

	@property
	def configurations(self):
		return self._configurations
