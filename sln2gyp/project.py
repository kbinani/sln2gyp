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
			self._extract_source_files(xmldom, project)
			self._extract_configurations(xmldom, project)
			self._parse_configuration_property_group(xmldom, project)

		def _extract_source_files(self, xmldom, project):
			comp = xmldom.getElementsByTagName('ClCompile')
			incl = xmldom.getElementsByTagName('ClInclude')

			def append_file(element_list):
				for element in element_list:
					if element.hasAttribute('Include'):
						file = element.getAttribute('Include')
						project._sources.append(util.normpath(file))

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
			node_list = []
			for node in all_node_list:
				if node.getAttribute('Label') == 'Configuration':
					node_list.append(node)

			for node in node_list:
			 	condition = node.getAttribute('Condition')
			 	for config in project.configurations():
			 		if config.is_match(condition):
			 			value = node.getElementsByTagName('ConfigurationType').item(0).firstChild.nodeValue
			 			project._type.set(config, value)
			#TODO: parse other sections: <UseDebugLibraries>, <PlatformToolset>, <WholeProgramOptimization>, and <CharacterSet>

	def __init__(self, file, name, guid):
		self._file = file
		self._guid = guid
		self._name = name
		self._sources = []
		self._configurations = []
		self._type = Property('Application')
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

	def type(self):
		return self._type
