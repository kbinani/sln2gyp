import os.path
import json
from project import Project

class Generator:
	def __init__(self):
		''

	def generate_gyp(self, solution):
		self._generate_sln_gyp(solution)
		for p in solution.projects():
			self._generate_proj_gyp(solution, p)

	def _generate_sln_gyp(self, solution):
		abs_gyp_path, _ = os.path.splitext(solution.solution_file())
		abs_gyp_path = abs_gyp_path + '.gyp'

		gyp = {}

		# generate 'includes' section
		gyp['includes'] = self._generate_sln_inclues(solution)

		f = open(abs_gyp_path, 'w')
		f.write(json.dumps(gyp, indent = 4))

	def _generate_sln_inclues(self, solution):
		includes = []
		for p in solution.projects():
			abs_project_file = p.project_file()
			abs_gyp_file, _ = os.path.splitext(abs_project_file)
			abs_gyp_file = abs_gyp_file + '.gypi'
			relative_path_to_sln = os.path.relpath(abs_gyp_file, solution.solution_dir())
			includes.append(relative_path_to_sln)
		return includes

	def _generate_proj_gyp(self, solution, project):
		abs_gyp_path, _ = os.path.splitext(project.project_file())
		abs_gyp_path = abs_gyp_path + '.gypi'

		target = {
			'target_name': project.name(),
			'type': self._get_gyp_type_from_vs_type(self._get_project_type(project)),
			'sources': self._generate_proj_sources(project),
			'configurations': self._generate_proj_configurations(project),
		}
		gyp = {}
		gyp['targets'] = [target]

		f = open(abs_gyp_path, 'w')
		f.write(json.dumps(gyp, indent = 4))

	def _generate_proj_sources(self, project):
		sources = []
		for source_file in project.sources():
			sources.append(source_file)
		return sources

	def _get_project_type(self, project):
		"""
		Get project type, if all configurations have same types.
		"""
		value = None
		for config in project.configurations():
			v = project.type().get(config)
			if value == None:
				value = v
			else:
				if value != v:
					return 'none'
		if value == None:
			return 'none'
		else:
			return value

	def _get_gyp_type_from_vs_type(self, vs_configuration_type):
		if vs_configuration_type == 'Application':
			return 'executable'
		elif vs_configuration_type == 'StaticLibrary':
			return 'static_library'
		else:
			return 'none'

	def _generate_proj_configurations(self, project):
		name_list = set()
		for c in project.configurations():
			name_list.add(c.configuration())

		#TODO: consider the case: same name but difference platform
		configurations = {}
		for name in name_list:
			configurations[name] = {}

		return configurations