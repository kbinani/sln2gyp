import xml.dom.minidom
import os.path
import util
from configuration import Configuration, Property

class Project:
	class ParserFactory:
		def __init__(self):
			pass

		def create_by_version(self, tools_version):
			if tools_version == '4.0':
				return Project.VC2012ProjectParser(tools_version)
			else:
				return Project.Parser()

	class Parser:
		def __init__(self, tools_version):
			self._tools_version = tools_version

		def parse(self, xmldom, project):
			pass

	class VC2012ProjectParser(Parser):
		def parse(self, xmldom, project):
			project._tools_version = self._tools_version
			self._extract_configurations(xmldom, project)
			self._extract_source_files(xmldom, project)
			self._parse_configuration_property_group(xmldom, project)
			self._parse_item_definition_group(xmldom, project)

		def _extract_source_files(self, xmldom, project):
			comp = xmldom.getElementsByTagName('ClCompile')
			incl = xmldom.getElementsByTagName('ClInclude')

			def append_file(element_list):
				for element in element_list:
					if element.hasAttribute('Include'):
						file = element.getAttribute('Include')
						project._sources.append(util.normpath(file))

						precompiled_header_node_list = element.getElementsByTagName('PrecompiledHeader')
						for node in precompiled_header_node_list:
							precompiled_source_option = util.xml2obj(node)
							if precompiled_source_option == 'Create':
								if node.hasAttribute('Condition'):
									condition = node.getAttribute('Condition')
									for config in project.configurations():
										if config.is_match(condition):
											project._precompiled_source.set(config, file)
								else:
									project._precompiled_source.set_default(file)

			append_file(comp)
			append_file(incl)

		def _extract_configurations(self, xmldom, project):
			node_list = xmldom.getElementsByTagName('ProjectConfiguration')
			for node in node_list:
				name_node = node.getElementsByTagName('Configuration')
				platform_node = node.getElementsByTagName('Platform')
				if name_node == None or platform_node == None:
					continue
				if len(name_node) == 0 or len(platform_node) == 0:
					continue

				name = name_node.item(0).firstChild.nodeValue
				platform = platform_node.item(0).firstChild.nodeValue

				configuration = Configuration(name, platform)
				project._configurations.append(configuration)

		def _parse_configuration_property_group(self, xmldom, project):
			all_node_list = xmldom.getElementsByTagName('PropertyGroup')

			configuration_node_list = []
			bare_node_list = []
			for node in all_node_list:
				if node.hasAttribute('Label'):
					label = node.getAttribute('Label')
					if label == 'Configuration':
						configuration_node_list.append(node)
				else:
					bare_node_list.append(node)

			for node in configuration_node_list:
	 			value = util.xml2obj(node)
				if node.hasAttribute('Condition'):
				 	condition = node.getAttribute('Condition')
				 	for config in project.configurations():
				 		if config.is_match(condition):
				 			project._project_options.set(config, value)
				else:
					project._project_options.set_default(value)

			for node in bare_node_list:
				value = util.xml2obj(node)
				if node.hasAttribute('Condition'):
					condition = node.getAttribute('Condition')
					for config in project.configurations():
						if config.is_match(condition):
							project._properties.set(config, value)
				else:
					project._properties.set_default(value)

		def _parse_item_definition_group(self, xmldom, project):
			node_list = xmldom.getElementsByTagName('ItemDefinitionGroup')
			for node in node_list:
				condition = node.getAttribute('Condition')
				definition = util.xml2obj(node)

				link_options = {}
				if 'Link' in definition:
					link_options = self._transform_link_dict_style(definition['Link'])

				compile_options = {}
				if 'ClCompile' in definition:
					compile_options = self._transform_clcompile_dict_style(definition['ClCompile'])

				for config in project.configurations():
					if config.is_match(condition):
						project._link_options.set(config, link_options)
						project._compile_options.set(config, compile_options)

		def _transform_link_dict_style(self, link_dict):
			split_with_semicollon = [
				'AdditionalDependencies',
			]
			return self._split_semicollon_separated_string_into_list_in_a_dict(link_dict, split_with_semicollon)

		def _transform_clcompile_dict_style(self, clcompile_dict):
			split_with_semicollon = [
				'PreprocessorDefinitions',
				'AdditionalIncludeDirectories',
				'ForcedIncludeFiles',
			]
			return self._split_semicollon_separated_string_into_list_in_a_dict(clcompile_dict, split_with_semicollon)

		def _split_semicollon_separated_string_into_list_in_a_dict(self, dictionary, key_names_to_split):
			for key in key_names_to_split:
				if key in dictionary:
					value = dictionary[key].strip()
					if value == '':
						dictionary[key] = []
					else:
						dictionary[key] = value.split(';')
			return dictionary

	def __init__(self, file, name, guid):
		self._file = file
		self._guid = guid
		self._name = name
		self._sources = []
		self._configurations = []

		# represents the <PropertyGroup Label="Configuartion"> section
		self._project_options = Property({})

		self._dependencies = []

		# represents the <Link> section under <ItemDefinitionGroup> section
		self._link_options = Property({})

		# represents the <ClCompile> section under <ItemDefinitionGroup> section
		self._compile_options = Property({})

		self._precompiled_source = Property(None)

		# represents the <Property Group> section
		self._properties = Property({})

		dom = xml.dom.minidom.parse(file)
		version = self._detect_project_version(dom)

		parser = Project.ParserFactory().create_by_version(version)
		parser.parse(dom, self)

	def _detect_project_version(self, xmldom):
		project_node_list = xmldom.getElementsByTagName('Project')
		if project_node_list == None:
			return None
		if project_node_list.length == 0:
			return None

		project_node = project_node_list.item(0)
		if project_node.hasAttribute('ToolsVersion'):
			return project_node.getAttribute('ToolsVersion')

		return None

	def sources(self):
		return self._sources

	def project_dir(self):
		return os.path.dirname(self._file)

	def project_file(self):
		return self._file

	def name(self):
		return self._name

	def guid(self):
		return self._guid

	def tools_version(self):
		return self._tools_version

	def configurations(self):
		return self._configurations

	@property
	def project_options(self):
		return self._project_options

	def dependencies(self):
		return self._dependencies

	@property
	def link_options(self):
		return self._link_options

	@property
	def compile_options(self):
		return self._compile_options
	
	def precompiled_source(self, configuration):
		return self._precompiled_source.get(configuration)

	@property
	def properties(self):
		return self._properties
