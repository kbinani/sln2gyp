import unittest
import os.path
import json
import sln2gyp

class GeneratorTest(unittest.TestCase):
	def test_generate_gyp(self):
		sln_file = 'test/fixtures/vs2012/dependency/Win32Project1/Win32Project1.sln'
		abs_sln_file = os.path.abspath(sln_file)
		abs_sln_dir = os.path.dirname(abs_sln_file)

		solution = sln2gyp.Solution(abs_sln_file)
		generator = sln2gyp.Generator()
		generator.generate_gyp(solution)

		# root gyp file, correspoinding to 'Win32Project1.sln'
		expected_root_gyp_path = os.path.join(abs_sln_dir, 'Win32Project1.gyp')
		self.assertTrue(os.path.exists(expected_root_gyp_path))

		expected_contents = {
			'targets': [
				{
					'target_name': 'All',
					'type': 'none',
					'dependencies': [
						'Win32Project1/Win32Project1.gyp:Win32Project1',
						'depend/depend.gyp:depend',
					]
				}
			]
		}
		actual_contents = json.loads(open(expected_root_gyp_path).read())
		self.assertEqual(expected_contents, actual_contents)

		# dependent gypi file, correspoinding to 'Win32Project1/Win32Project1.vcxproj'
		def assert_Win32Project_proj():
			expected_depend_gyp_path = os.path.join(abs_sln_dir, 'Win32Project1/Win32Project1.gyp')
			self.assertTrue(os.path.exists(expected_depend_gyp_path))

			expected_contents = {
				'targets': [
					{
						'target_name': 'Win32Project1',
						'type': 'executable',
						'dependencies': [
							'../depend/depend.gyp:depend',
						],
						'sources': [
							'stdafx.cpp',
							'Win32Project1.cpp',
							'Resource.h',
							'stdafx.h',
							'targetver.h',
							'Win32Project1.h',
						],
						'configurations': {
							'Debug': {
								'msvs_settings': {
									'VCCLCompilerTool': {
										'Optimization': 0,
									},
								},
							},
							'Release': {
								'msvs_settings': {
									'VCCLCompilerTool': {
										'WholeProgramOptimization': 'true',
										'Optimization': 2,
									}
								},
							},
						},
						'msvs_settings': {
							'VCLinkerTool': {
								'SubSystem': 2,
								'AdditionalDependencies': [
									'%(AdditionalDependencies)',
								],
							},
							'VCCLCompilerTool': {
								'UsePrecompiledHeader': 2,
								'WarningLevel': 3,
							}
						},
						'msvs_precompiled_source': 'stdafx.cpp',
					}
				]
			}
			actual_contents = json.loads(open(expected_depend_gyp_path).read())
			self.assertEqual(expected_contents, actual_contents)
		assert_Win32Project_proj()

		def assert_depend_proj():
			expected_depend_gyp_path = os.path.join(abs_sln_dir, 'depend/depend.gyp')
			self.assertTrue(os.path.exists(expected_depend_gyp_path))

			expected_contents = {
				'targets': [
					{
						'target_name': 'depend',
						'type': 'static_library',
						'sources': [
							'stdafx.cpp',
							'stdafx.h',
							'targetver.h',
						],
						'configurations': {
							'Debug': {
							},
							'Release': {
							},
						},
						'msvs_settings': {
							'VCLinkerTool': {
								'AdditionalDependencies': [
									'%(AdditionalDependencies)',
								],
							}
						}
					}
				]
			}
			actual_contents = json.loads(open(expected_depend_gyp_path).read())
			self.assertEqual(expected_contents, actual_contents)
		assert_depend_proj()
