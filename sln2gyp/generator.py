import os.path
import json
import re
from project import Project
import util

class Generator:
	def __init__(self):
		pass

	def generate_gyp(self, solution):
		self._generate_sln_gyp(solution)
		for p in solution.projects():
			self._generate_proj_gyp(solution, p)

	def _generate_sln_gyp(self, solution):
		abs_gyp_path, _ = os.path.splitext(solution.solution_file())
		abs_gyp_path = abs_gyp_path + '.gyp'

		gyp = {
			'targets': [
				{
					'target_name': 'All',
					'type': 'none',
					'dependencies': self._generate_dependencies(solution)
				}
			]
		}

		f = open(abs_gyp_path, 'w')
		f.write(json.dumps(gyp, indent = 4))

	def _generate_dependencies(self, solution):
		includes = []
		for p in solution.projects():
			abs_project_file = p.project_file()
			abs_gyp_file, _ = os.path.splitext(abs_project_file)
			abs_gyp_file = abs_gyp_file + '.gyp:' + p.name()
			relative_path_to_sln = util.normpath(os.path.relpath(abs_gyp_file, solution.solution_dir()))
			includes.append(relative_path_to_sln)
		return includes

	def _generate_proj_gyp(self, solution, project):
		abs_gyp_path, _ = os.path.splitext(project.project_file())
		abs_gyp_path = abs_gyp_path + '.gyp'

		target = {
			'target_name': project.name(),
			'type': self._get_gyp_type_from_vs_type(self._get_project_type(project)),
			'sources': self._generate_proj_sources(project),
			'configurations': self._generate_proj_configurations(project),
		}

		dependencies = self._generate_proj_dependencies(solution, project)
		if len(dependencies) > 0:
			target['dependencies'] = dependencies
		common_msvs_settings = self._generate_proj_common_msvs_settings(project)
		if len(common_msvs_settings) > 0:
			target['msvs_settings'] = common_msvs_settings

		for config in project.configurations():
			config_msvs_settings = self._generate_proj_msvs_settings(project, [config])
			extracted_msvs_settings = util.extract_hash_diff(common_msvs_settings, config_msvs_settings)
			if len(extracted_msvs_settings) > 0:
				target['configurations'][config.configuration()]['msvs_settings'] = extracted_msvs_settings

		gyp = {}
		gyp['targets'] = [target]

		f = open(abs_gyp_path, 'w')
		f.write(json.dumps(gyp, indent = 4))

	def _generate_proj_dependencies(self, solution, project):
		dependencies = []
		for dep_guid in project.dependencies():
			for p in solution.projects():
				if p.guid() == project.guid():
					continue
				if p.guid() == dep_guid:
					dep_proj_path = p.project_file()
					dep_gyp_name, ext = os.path.splitext(dep_proj_path)
					dep_gyp_path = dep_gyp_name + '.gyp'
					rel_gyp_path = os.path.relpath(dep_gyp_path, project.project_dir())
					dependencies.append(rel_gyp_path + ":" + p.name())
		return dependencies

	def _generate_proj_common_msvs_settings(self, project):
		return self._generate_proj_msvs_settings(project, project.configurations())

	def _generate_proj_msvs_settings(self, project, configurations):
		msvs_settings = {}

		# VCLinkerTool
		def generate_vclinkertool_section():
			section = {}
			link_options = project.link_options

			# SubSystem
			subsystem = link_options.get_common_value_for_configurations(configurations, 'SubSystem')
			if subsystem != None:
				section['SubSystem'] = self._get_subsystem(subsystem)

			# AdditionalDependencies
			section['AdditionalDependencies'] = ['%(AdditionalDependencies)']

			return section

		vclinkertool = generate_vclinkertool_section()
		if len(vclinkertool) > 0:
			msvs_settings['VCLinkerTool'] = vclinkertool

		# VCCLCompilerTool
		def generate_vcclcompilertool_section():
			section = {}
			compile_options = project.compile_options

			use_precompiled_header = compile_options.get_common_value_for_configurations(configurations, 'PrecompiledHeader')
			if use_precompiled_header != None:
				section['UsePrecompiledHeader'] = self._get_use_precompiled_header(use_precompiled_header)

			warning_level = compile_options.get_common_value_for_configurations(configurations, 'WarningLevel')
			if warning_level != None:
				section['WarningLevel'] = self._get_warning_level(warning_level)

			whole_program_optimization = project.project_options.get_common_value_for_configurations(configurations, 'WholeProgramOptimization')
			if whole_program_optimization != None:
				section['WholeProgramOptimization'] = whole_program_optimization

			return section

		vcclcompilertool = generate_vcclcompilertool_section()
		if len(vcclcompilertool) > 0:
			msvs_settings['VCCLCompilerTool'] = vcclcompilertool

		return msvs_settings

	def _get_subsystem(self, subsystem_string):
		if subsystem_string == 'Windows':
			return 2
		elif subsystem_string == 'Console':
			return 1
		elif subsystem_string == 'Native':
			return 3
		elif subsystem_string == 'EFI Application':
			return 4
		elif subsystem_string == 'EFI Boot Service Driver':
			return 5
		elif subsystem_string == 'EFI ROM':
			return 6
		elif subsystem_string == 'EFI Runtime':
			return 7
		elif subsystem_string == 'POSIX':
			#TODO(kbinani): gyp does not support 'POSIX' subsystem type
			return 0
		else:
			return 0

	def _get_use_precompiled_header(self, precompiled_header_string):
		if precompiled_header_string == 'Use':
			return 2
		elif precompiled_header_string == 'Create':
			return 1
		elif precompiled_header_string == 'NotUsing':
			return 0
		else:
			return None

	def _get_warning_level(self, warning_level):
		m = re.compile('Level(?P<level>[0-9]*)').search(warning_level)
		return int(m.group('level'))

	def _generate_proj_sources(self, project):
		sources = []
		for source_file in project.sources():
			sources.append(source_file)
		return sources

	def _get_project_type(self, project):
		value = project.project_options.get_common_value_for_configurations(project.configurations(), 'ConfigurationType')
		if value == None:
			return 'none'
		else:
			return value

	def _get_gyp_type_from_vs_type(self, vs_configuration_type):
		if vs_configuration_type == 'Application':
			return 'executable'
		elif vs_configuration_type == 'StaticLibrary':
			return 'static_library'
		elif vs_configuration_type == 'DynamicLibrary':
			return 'dynamic_library'
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
