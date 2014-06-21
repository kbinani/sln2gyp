import unittest
import os.path
import sln2gyp

class SolutionTestCase(unittest.TestCase):
	def setUp(self):
		self._sln_file = 'test/fixtures/simple2012/Win32Project1/Win32Project1.sln'
		self._abs_sln_file = os.path.abspath(self._sln_file)
		self._abs_sln_dir = os.path.dirname(self._abs_sln_file)

		self._solution = sln2gyp.Solution(self._sln_file)

	def test_parse_vs2012_project_test(self):
		self.assertEqual(os.path.dirname(self._abs_sln_file), self._solution.solution_dir())
		self.assertEqual(self._abs_sln_file, self._solution.solution_file())

		# assert Solution#configurations
		def assert_configurations():
			configurations = self._solution.configurations()
			self.assertEqual(2, len(configurations))
			self.assertEqual('Debug', configurations[0].configuration())
			self.assertEqual('Win32', configurations[0].platform())
			self.assertEqual('Release', configurations[1].configuration())
			self.assertEqual('Win32', configurations[1].platform())
		assert_configurations()

		# assert Solution#projects
		def assert_projects():
			self.assertEqual(1, len(self._solution.projects()))

			# assert Solution#projects()[0]
			project = self._solution.projects()[0]
			def assert_project():
				expected_project_dir = self._abs_sln_dir + '/Win32Project1'
				self.assertEqual(expected_project_dir, project.project_dir())

				expected_project_file = expected_project_dir + '/Win32Project1.vcxproj'
				self.assertEqual(expected_project_file, project.project_file())

				self.assertEqual('Win32Project1', project.name())
				self.assertEqual('{D5FE8C9E-25D9-43C1-A4E8-DE7ECBF2F02F}', project.guid())
				self.assertEqual('4.0', project.tools_version())

				def assert_options_debug():
					debug = sln2gyp.Configuration.create_from_string('Debug|Win32')

					link_options = project.link_options.get(debug)
					compile_options = project.compile_options.get(debug)

					self.assertEqual('Windows', link_options['SubSystem'])
					self.assertEqual('Disabled', compile_options['Optimization'])

					self.assertEqual('stdafx.cpp', project.precompiled_source(debug))
				assert_options_debug()

				def assert_options_release():
					release = sln2gyp.Configuration.create_from_string('Release|Win32')

					link_options = project.link_options.get(release)
					compile_options = project.compile_options.get(release)

					self.assertEqual('Windows', link_options['SubSystem'])
					self.assertEqual('MaxSpeed', compile_options['Optimization'])

					self.assertEqual('stdafx.cpp', project.precompiled_source(release))
				assert_options_release()
			assert_project()

			def assert_sources():
				source_list = project.sources()

				self.assertEqual(6, len(source_list))
				self.assertEqual('stdafx.cpp', source_list[0])
				self.assertEqual('Win32Project1.cpp', source_list[1])
				self.assertEqual('Resource.h', source_list[2])
				self.assertEqual('stdafx.h', source_list[3])
				self.assertEqual('targetver.h', source_list[4])
				self.assertEqual('Win32Project1.h', source_list[5])
			assert_sources()

			def assert_configurations():
				configurations = project.configurations()
				self.assertEqual(2, len(configurations))

				first = configurations[0]
				self.assertEqual('Debug', first.configuration())
				self.assertEqual('Win32', first.platform())

				second = configurations[1]
				self.assertEqual('Release', second.configuration())
				self.assertEqual('Win32', second.platform())
			assert_configurations()

			def assert_type():
				options = project.project_options

				debug = sln2gyp.Configuration('Debug', 'Win32')
				self.assertEqual('Application', options.get(debug)['ConfigurationType'])

				release = sln2gyp.Configuration('Release', 'Win32')
				self.assertEqual('Application', options.get(release)['ConfigurationType'])
			assert_type()
		assert_projects()

	def test_get_by_guid(self):
		guid = '{D5FE8C9E-25D9-43C1-A4E8-DE7ECBF2F02F}'
		project = self._solution.get_by_guid(guid)
		self.assertTrue(project != None)
		self.assertEqual(guid, project.guid())

		project = self._solution.get_by_guid('')
		self.assertTrue(project == None)

class SolutionWithDependencyTestCase(unittest.TestCase):
	def setUp(self):
		self._sln_file = 'test/fixtures/vs2012/dependency/Win32Project1/Win32Project1.sln'
		self._solution = sln2gyp.Solution(self._sln_file)

	def test(self):
		self.assertEqual(2, len(self._solution.projects()))
		win32project = self._solution.projects()[0]
		depend = self._solution.projects()[1]

		self.assertEqual(1, len(win32project.dependencies()))
		self.assertEqual(0, len(depend.dependencies()))

		self.assertEqual(depend.guid(), win32project.dependencies()[0])
