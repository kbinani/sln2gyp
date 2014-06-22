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
			relative_path_to_sln = util.normpath(os.path.relpath(abs_gyp_file, solution.solution_dir()))
			includes.append(relative_path_to_sln + ".gyp:" + p.name())
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
		common_msvs_settings = self._generate_proj_msvs_settings(project, project.configurations())
		if len(common_msvs_settings) > 0:
			target['msvs_settings'] = common_msvs_settings
		common_msvs_precompiled_source = self._generate_proj_msvs_precompiled_source(project, project.configurations())
		if common_msvs_precompiled_source != None:
			target['msvs_precompiled_source'] = common_msvs_precompiled_source
		common_msbuild_toolset = self._generate_proj_msbuild_toolset(project, project.configurations())
		if common_msbuild_toolset != None:
			target['msbuild_toolset'] = common_msbuild_toolset
		common_msvs_configuration_attributes = self._generate_proj_msvs_configuration_attributes(project, project.configurations())
		if common_msvs_configuration_attributes != None:
			target['msvs_configuration_attributes'] = common_msvs_configuration_attributes
		common_include_dirs = self._generate_proj_include_dirs(project, project.configurations())
		if common_include_dirs != None:
			target['include_dirs'] = common_include_dirs

		for config in project.configurations():
			config_msvs_settings = self._generate_proj_msvs_settings(project, [config])
			extracted_msvs_settings = util.extract_hash_diff(common_msvs_settings, config_msvs_settings)
			if len(extracted_msvs_settings) > 0:
				target['configurations'][config.configuration()]['msvs_settings'] = extracted_msvs_settings

			config_msvs_precompiled_source = self._generate_proj_msvs_precompiled_source(project, [config])
			if config_msvs_precompiled_source != None and config_msvs_precompiled_source != common_msvs_precompiled_source:
				target['configurations'][config.configuration()]['msvs_precompiled_source'] = config_msvs_precompiled_source

			config_msbuild_toolset = self._generate_proj_msbuild_toolset(project, [config])
			if config_msbuild_toolset != None and config_msbuild_toolset != common_msbuild_toolset:
				target['configurations'][config.configuration()]['msbuild_toolset'] = config_msbuild_toolset

			config_msvs_configuration_attributes = self._generate_proj_msvs_configuration_attributes(project, [config])
			extracted_msvs_configuration_attributes = util.extract_hash_diff(common_msvs_configuration_attributes, config_msvs_configuration_attributes)
			if len(extracted_msvs_configuration_attributes) > 0:
				target['configurations'][config.configuration()]['msvs_configuration_attributes'] = extracted_msvs_configuration_attributes

			config_include_dirs = self._generate_proj_include_dirs(project, [config])
			if config_include_dirs != None and config_include_dirs != common_include_dirs:
				target['configurations'][config.configuration()]['include_dirs'] = config_include_dirs

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
					rel_gyp_path = util.normpath(os.path.relpath(dep_gyp_path, project.project_dir()))
					dependencies.append(rel_gyp_path + ":" + p.name())
		return dependencies

	def _generate_proj_include_dirs(self, project, configurations):
		include_dirs = project.compile_options.get_common_value_for_configurations(configurations, 'AdditionalIncludeDirectories')
		if include_dirs != None:
			if len(include_dirs) > 0:
				result = []
				for d in include_dirs:
					result.append(util.normpath(d))
				return result
		return None

	def _generate_proj_msvs_configuration_attributes(self, project, configurations):
		msvs_configuration_attributes = {}

		character_set = self._get_character_set(project.project_options.get_common_value_for_configurations(configurations, 'CharacterSet'))
		if character_set != None:
			msvs_configuration_attributes['CharacterSet'] = character_set

		if len(msvs_configuration_attributes) > 0:
			return msvs_configuration_attributes
		else:
			return None

	def _generate_proj_msbuild_toolset(self, project, configurations):
		is_first = True
		msbuild_toolset = None
		for config in configurations:
			project_options = project.project_options.get(config)
			if 'PlatformToolset' in project_options:
				toolset = project_options['PlatformToolset']
				if is_first:
					msbuild_toolset = toolset
				else:
					if toolset != msbuild_toolset:
						return None
		return msbuild_toolset

	def _generate_proj_msvs_precompiled_source(self, project, configurations):
		is_first = True
		precompiled_source = None
		for config in configurations:
			source = project.precompiled_source(config)
			if is_first:
				precompiled_source = source
			else:
				if source != precompiled_source:
					return None
		return precompiled_source

	def _generate_proj_msvs_settings(self, project, configurations):
		msvs_settings = {}

		# VCLinkerTool
		def generate_vclinkertool_section():
			section = {}
			link_options = project.link_options
			project_options = project.project_options
			properties = project.properties

			# SubSystem
			subsystem = link_options.get_common_value_for_configurations(configurations, 'SubSystem')
			if subsystem != None:
				section['SubSystem'] = self._get_subsystem(subsystem)

			# AdditionalDependencies
			additional_dependencies = link_options.get_common_value_for_configurations(configurations, 'AdditionalDependencies')
			if additional_dependencies == None:
				section['AdditionalDependencies'] = ['%(AdditionalDependencies)']
			elif len(additional_dependencies) > 0:
				section['AdditionalDependencies'] = additional_dependencies

			use_debug_libraries = link_options.get_common_value_for_configurations(configurations, 'GenerateDebugInformation')
			if use_debug_libraries != None:
				section['GenerateDebugInformation'] = use_debug_libraries

			link_incremental = properties.get_common_value_for_configurations(configurations, 'LinkIncremental')
			if link_incremental != None:
				section['LinkIncremental'] = self._get_link_incremental(link_incremental)

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

			optimization = compile_options.get_common_value_for_configurations(configurations, 'Optimization')
			if optimization != None:
				section['Optimization'] = self._get_optimization(optimization)

			preprocessor_defines = compile_options.get_common_value_for_configurations(configurations, 'PreprocessorDefinitions')
			if preprocessor_defines != None:
				section['PreprocessorDefinitions'] = preprocessor_defines

			return section

		vcclcompilertool = generate_vcclcompilertool_section()
		if len(vcclcompilertool) > 0:
			msvs_settings['VCCLCompilerTool'] = vcclcompilertool

		if len(msvs_settings) > 0:
			return msvs_settings
		else:
			return {}

	def _get_link_incremental(self, link_incremental_string):
		if link_incremental_string == 'false':
			return 1
		elif link_incremental_string == 'true':
			return 2
		else:
			return None

	def _get_character_set(self, character_set_string):
		if character_set_string == 'Unicode':
			return 1
		elif character_set_string == 'MultiByte':
			return 2
		else:
			return None

	def _get_optimization(self, optimization_string):
		if optimization_string == 'Disabled':
			return 0
		elif optimization_string == 'MinSpace':
			return 1
		elif optimization_string == 'MaxSpeed':
			return 2
		elif optimization_string == 'Full':
			return 3
		else:
			return None

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
