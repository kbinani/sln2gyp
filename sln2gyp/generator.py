import os.path
import json
import re
from project import Project
import util
from msvs_option_converter import MsvsOptionConverter

class Generator:
	def __init__(self):
		pass

	def generate_gyp(self, solution):
		self._generate_sln_gyp(solution)
		for p in solution.projects:
			self._generate_proj_gyp(solution, p)

	def _generate_sln_gyp(self, solution):
		abs_gyp_path, _ = os.path.splitext(solution.solution_file)
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
		for p in solution.projects:
			abs_project_file = p.project_file
			abs_gyp_file, _ = os.path.splitext(abs_project_file)
			relative_path_to_sln = util.normpath(os.path.relpath(abs_gyp_file, solution.solution_dir))
			includes.append(relative_path_to_sln + ".gyp:" + p.name)
		return includes

	def _generate_proj_gyp(self, solution, project):
		abs_gyp_path, _ = os.path.splitext(project.project_file)
		abs_gyp_path = abs_gyp_path + '.gyp'

		target = {
			'target_name': project.name,
			'type': self._get_project_type(project),
			'sources': self._generate_proj_sources(project),
			'configurations': self._generate_proj_configurations(project),
		}

		dependencies = self._generate_proj_dependencies(solution, project)
		if len(dependencies) > 0:
			target['dependencies'] = dependencies
		common_msvs_settings = self._generate_proj_msvs_settings(project, project.configurations)
		if len(common_msvs_settings) > 0:
			target['msvs_settings'] = common_msvs_settings
		common_msvs_precompiled_source = self._generate_proj_msvs_precompiled_source(project, project.configurations)
		if common_msvs_precompiled_source != None:
			target['msvs_precompiled_source'] = common_msvs_precompiled_source
		common_msbuild_toolset = self._generate_proj_msbuild_toolset(project, project.configurations)
		if common_msbuild_toolset != None:
			target['msbuild_toolset'] = common_msbuild_toolset
		common_msvs_configuration_attributes = self._generate_proj_msvs_configuration_attributes(project, project.configurations)
		if common_msvs_configuration_attributes != None:
			target['msvs_configuration_attributes'] = common_msvs_configuration_attributes
		common_include_dirs = self._generate_proj_include_dirs(project, project.configurations)
		if common_include_dirs != None:
			target['include_dirs'] = common_include_dirs

		for config in project.configurations:
			config_msvs_settings = self._generate_proj_msvs_settings(project, [config])
			extracted_msvs_settings = util.extract_dict_diff(common_msvs_settings, config_msvs_settings)
			if len(extracted_msvs_settings) > 0:
				target['configurations'][config.configuration()]['msvs_settings'] = extracted_msvs_settings

			config_msvs_precompiled_source = self._generate_proj_msvs_precompiled_source(project, [config])
			if config_msvs_precompiled_source != None and config_msvs_precompiled_source != common_msvs_precompiled_source:
				target['configurations'][config.configuration()]['msvs_precompiled_source'] = config_msvs_precompiled_source

			config_msbuild_toolset = self._generate_proj_msbuild_toolset(project, [config])
			if config_msbuild_toolset != None and config_msbuild_toolset != common_msbuild_toolset:
				target['configurations'][config.configuration()]['msbuild_toolset'] = config_msbuild_toolset

			config_msvs_configuration_attributes = self._generate_proj_msvs_configuration_attributes(project, [config])
			extracted_msvs_configuration_attributes = util.extract_dict_diff(common_msvs_configuration_attributes, config_msvs_configuration_attributes)
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
		for dep_guid in project.dependencies:
			for p in solution.projects:
				if p.guid == project.guid:
					continue
				if p.guid == dep_guid:
					dep_proj_path = p.project_file
					dep_gyp_name, ext = os.path.splitext(dep_proj_path)
					dep_gyp_path = dep_gyp_name + '.gyp'
					rel_gyp_path = util.normpath(os.path.relpath(dep_gyp_path, project.project_dir))
					dependencies.append(rel_gyp_path + ":" + p.name)
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
		converter = MsvsOptionConverter()

		character_set = converter.convert('CharacterSet', project.project_options.get_common_value_for_configurations(configurations, 'CharacterSet'))
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

	def _generate_proj_msvs_settings_part(self, project, configurations, generate_options):
		section = {}
		converter = MsvsOptionConverter()

		for msvs_section_name, option in generate_options.items():
			option_source = option['option_source']
			value = option_source.get_common_value_for_configurations(configurations, msvs_section_name)
			if value != None:
				gyp_section_name = option['gyp_section_name'] if ('gyp_section_name' in option) else msvs_section_name
				section[gyp_section_name] = converter.convert(msvs_section_name, value)

		return section

	def _generate_proj_msvs_settings(self, project, configurations):
		msvs_settings = {}

		# VCLinkerTool
		def generate_vclinkertool_section():
			link_options = project.link_options
			project_options = project.project_options
			properties = project.properties

			generate_options = {
				'SubSystem': {
					'option_source': link_options,
				},
				'GenerateDebugInformation': {
					'option_source': link_options,
				},
				'LinkIncremental': {
					'option_source': properties,
				},
				'EnableCOMDATFolding': {
					'option_source': link_options,
				},
				'OptimizeReferences': {
					'option_source': link_options,
				},
			}
			section = self._generate_proj_msvs_settings_part(project, configurations, generate_options)

			# AdditionalDependencies
			additional_dependencies = link_options.get_common_value_for_configurations(configurations, 'AdditionalDependencies')
			if additional_dependencies == None:
				section['AdditionalDependencies'] = ['%(AdditionalDependencies)']
			elif len(additional_dependencies) > 0:
				section['AdditionalDependencies'] = additional_dependencies

			return section

		vclinkertool = generate_vclinkertool_section()
		if len(vclinkertool) > 0:
			msvs_settings['VCLinkerTool'] = vclinkertool

		# VCCLCompilerTool
		def generate_vcclcompilertool_section():
			compile_options = project.compile_options
			project_options = project.project_options

			generate_options = {
				'PrecompiledHeader': {
					'option_source': compile_options,
					'gyp_section_name': 'UsePrecompiledHeader',
				},
				'WarningLevel': {
					'option_source': compile_options,
				},
				'Optimization': {
					'option_source': compile_options,
				},
				'PreprocessorDefinitions': {
					'option_source': compile_options,
				},
				'DebugInformationFormat': {
					'option_source': compile_options,
				},
				'RuntimeLibrary': {
					'option_source': compile_options,
				},
				'FloatingPointModel': {
					'option_source': compile_options,
				},
				'AdditionalOptions': {
					'option_source': compile_options,
				},
				'ForcedIncludeFiles': {
					'option_source': compile_options,
				},
				'WholeProgramOptimization': {
					'option_source': project_options,
				},
				'SuppressStartupBanner': {
					'option_source': compile_options,
				},
				'TreatWarningAsError': {
					'option_source': compile_options,
					'gyp_section_name': 'WarnAsError',
				},
				'IntrinsicFunctions': {
					'option_source': compile_options,
					'gyp_section_name': 'EnableIntrinsicFunctions',
				},
				'FavorSizeOrSpeed': {
					'option_source': compile_options,
				},
				'OmitFramePointers': {
					'option_source': compile_options,
				},
				'EnableFiberSafeOptimizations': {
					'option_source': compile_options,
				},
				'UndefinePreprocessorDefinitions': {
					'option_source': compile_options,
				},
				'UndefineAllPreprocessorDefinitions': {
					'option_source': compile_options,
				},
				'IgnoreStandardIncludePath': {
					'option_source': compile_options,
				},
				'PreprocessKeepComments': {
					'option_source': compile_options,
					'gyp_section_name': 'KeepComments',
				},
				'MinimalRebuild': {
					'option_source': compile_options,
				},
				'SmallerTypeCheck': {
					'option_source': compile_options,
				},
				'BasicRuntimeChecks': {
					'option_source': compile_options,
				},
				'StructMemberAlignment': {
					'option_source': compile_options,
				},
				'BufferSecurityCheck': {
					'option_source': compile_options,
				},
				'FunctionLevelLinking': {
					'option_source': compile_options,
					'gyp_section_name': 'EnableFunctionLevelLinking',
				},
				'EnableEnhancedInstructionSet': {
					'option_source': compile_options,
				},
			}

			section = self._generate_proj_msvs_settings_part(project, configurations, generate_options)

			converter = MsvsOptionConverter()

			# workaround for gyp design. gyp does not recognize 'InlineFunctionExpansion' == 'Disabled', so add '/Ob0' option to 'AdditionalOptions'.
			inline_function_expansion = compile_options.get_common_value_for_configurations(configurations, 'InlineFunctionExpansion')
			if inline_function_expansion != None:
				if inline_function_expansion == 'Disabled':
					if 'AdditionalOptions' not in section:
						section['AdditionalOptions'] = ''
					section['AdditionalOptions'] = '/Ob0' if section['AdditionalOptions'] == '' else section['AdditionalOptions'] + ' /Ob0'
				else:
					section['InlineFunctionExpansion'] = converter.convert('InlineFunctionExpansion', inline_function_expansion)

			# create 'GeneratePreprocessedFile' section. The value of this option depends on two vcxprojc sections, <PreprocessToFile> and <PreprocessSuppressLineNumbers>.
			preprocess_to_file = compile_options.get_common_value_for_configurations(configurations, 'PreprocessToFile')
			preprocess_suppress_line_numbers = compile_options.get_common_value_for_configurations(configurations, 'PreprocessSuppressLineNumbers')
			generate_preprocessed_file = self._get_generate_preprocessed_file(preprocess_to_file, preprocess_suppress_line_numbers)
			if generate_preprocessed_file != None:
				section['GeneratePreprocessedFile'] = generate_preprocessed_file

			# workaround for gyp design. gyp does not recognize 'ExceptionHandling' == 'SyncCThrow', so add '/EHsc' option to 'AdditionalOptions'.
			exception_handling = compile_options.get_common_value_for_configurations(configurations, 'ExceptionHandling')
			if exception_handling != None:
				if exception_handling == 'SyncCThrow':
					if 'AdditionalOptions' not in section:
						section['AdditionalOptions'] = ''
					section['AdditionalOptions'] = '/EHsc' if section['AdditionalOptions'] == '' else section['AdditionalOptions'] + ' /EHsc'
				else:
					section['ExceptionHandling'] = converter.convert('ExceptionHandling', exception_handling)

			return section

		vcclcompilertool = generate_vcclcompilertool_section()
		if len(vcclcompilertool) > 0:
			msvs_settings['VCCLCompilerTool'] = vcclcompilertool

		if len(msvs_settings) > 0:
			return msvs_settings
		else:
			return {}

	def _get_generate_preprocessed_file(self, preprocess_to_file, preprocess_suppress_line_numbers):
		if preprocess_to_file == None or preprocess_suppress_line_numbers == None:
			return None
		if preprocess_to_file != 'true' and preprocess_to_file != 'false':
			return None
		if preprocess_suppress_line_numbers != 'true' and preprocess_suppress_line_numbers != 'false':
			return None

		if preprocess_to_file == 'false':
			return 0
		else:
			if preprocess_suppress_line_numbers == 'true':
				return 2
			else:
				return 1

	def _generate_proj_sources(self, project):
		sources = []
		for source_file in project.sources:
			sources.append(source_file)
		return sources

	def _get_project_type(self, project):
		converter = MsvsOptionConverter()
		project_options = project.project_options
		msvs_section_name = 'ConfigurationType'
		configuration_type = project_options.get_common_value_for_configurations(project.configurations, msvs_section_name)

		value = converter.convert(msvs_section_name, configuration_type)
		if value == None:
			return 'none'
		else:
			return value

	def _generate_proj_configurations(self, project):
		name_list = set()
		for c in project.configurations:
			name_list.add(c.configuration())

		#TODO: consider the case: same name but difference platform
		configurations = {}
		for name in name_list:
			configurations[name] = {}

		return configurations
