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
										'PreprocessorDefinitions': [
											'WIN32',
											'_DEBUG',
											'_WINDOWS',
											'%(PreprocessorDefinitions)',
										],
										'DebugInformationFormat': 3,
										'RuntimeLibrary': 1,
										'FloatingPointModel': 0,
										'AdditionalOptions': '-Zm123 /Ob0',
										'SuppressStartupBanner': 'false',
										'WarnAsError': 'true',
										'UndefinePreprocessorDefinitions': [
											'FOO',
											'%(UndefinePreprocessorDefinitions)',
										],
										'UndefineAllPreprocessorDefinitions': 'false',
										'IgnoreStandardIncludePath': 'false',
										'GeneratePreprocessedFile': 0,
										'KeepComments': 'true',
										'MinimalRebuild': 'false',
										'SmallerTypeCheck': 'true',
										'BasicRuntimeChecks': 3,
										'StructMemberAlignment': 0,
										'BufferSecurityCheck': 'true',
										'FloatingPointExceptions': 'true',
										'DisableLanguageExtensions': 'false',
										'TreatWChar_tAsBuiltInType': 'true',
										'ForceConformanceInForLoopScope': 'true',
										'RuntimeTypeInfo': 'true',
										'PrecompiledHeaderFile': '$(IntDir)$(TargetName).pch',
										'ExpandAttributedSource': 'true',
										'AssemblerOutput': 1,
										'AssemblerListingLocation': '$(IntDir)',
										'ObjectFile': '$(IntDir)',
										'ProgramDataBaseFileName': '$(IntDir)vc$(PlatformToolsetVersion).pdb',
										'GenerateXMLDocumentationFiles': 'true',
										'XMLDocumentationFileName': '$(IntDir)',
										'BrowseInformation': 1,
										'BrowseInformationFile': '$(IntDir)',
										'CallingConvention': 0,
										'CompileAs': 0,
										'DisableSpecificWarnings': [
											'4995', '4996',
										],
										'ForcedUsingFiles': [
											'dummyA',
											'dummyB',
										],
										'ShowIncludes': 'true',
										'UseFullPaths': 'true',
										'OmitDefaultLibName': 'false',
										'ErrorReporting': 0,
									},
									'VCLinkerTool': {
										'GenerateDebugInformation': 'true',
										'LinkIncremental': 2,
										'OutputFile': '$(OutDir)$(TargetName)$(TargetExt)',
										'ShowProgress': 1,
										'SuppressStartupBanner': 'true',
										'IgnoreImportLibrary': 'false',
										'RegisterOutput': 'false',
										'PerUserRedirection': 'false',
										'LinkLibraryDependencies': 'true',
										'UseLibraryDependencyInputs': 'false',
										'IgnoreAllDefaultLibraries': 'false',
										'AdditionalDependencies': [
											'libcmtd.lib',
											'winmm.lib',
											'%(AdditionalDependencies)',
										],
										'IgnoreDefaultLibraryNames': [
											'libcmtd.lib',
										],
										'ModuleDefinitionFile': 'Win32Project1.def',
										'AddModuleNamesToAssembly': [
											'dummyA',
											'dummyB',
										],
										'EmbedManagedResourceFile': [
											'dummyC',
											'dummyD',
										],
										'ForceSymbolReferences': [
											'_dummy_symbol_1',
											'_dummy_symbol_2',
										],
										'DelayLoadDLLs': [
											'd3d9.dll',
											'd3dx9d.dll',
										],
										'AssemblyLinkResource': [
											'dummyE',
											'dummyF',
										],
										'GenerateManifest': 'true',
										'ManifestFile': '$(IntDir)$(TargetName)$(TargetExt).intermediate.manifest',
										'AdditionalManifestDependencies': [
											'"type=\'win32\' name=\'Microsoft.Windows.Common-Controls\' version=\'6.0.0.0\' processorArchitecture=\'x86\' publicKeyToken=\'6595b64144ccf1df\' language=\'*\'"',
											'"type=\'win32\' name=\'Microsoft.Windows.Common-Controls\' version=\'6.0.0.0\' processorArchitecture=\'x86\' publicKeyToken=\'6595b64144ccf1df\' language=\'neutral\'"',
										],
										'AllowIsolation': 'true',
										'EnableUAC': 'true',
										'UACExecutionLevel': 0,
										'UACUIAccess': 'false',
										'ProgramDatabaseFile': '$(OutDir)$(TargetName).pdb',
										'StripPrivateSymbols': '$(OutDir)$(TargetName).stripped.pdb',
										'GenerateMapFile': 'true',
										'MapFileName': '$(OutDir)$(TargetName).map',
										'MapExports': 'false',
										'AssemblyDebug': 1,
										'HeapReserveSize': '1048576',
										'HeapCommitSize': '4096',
										'StackReserveSize': '2097152',
										'StackCommitSize': '8192',
										'LargeAddressAware': 1,
										'TerminalServerAware': 1,
										'SwapRunFromCD': 'false',
										'SwapRunFromNet': 'false',
										'Driver': 0,
										'FunctionOrder': 'Win32Project1.order',
										'ProfileGuidedDatabase': '$(OutDir)$(TargetName).pgd',
										'MidlCommandFile': 'Win32Project1.midl',
										'IgnoreEmbeddedIDL': 'false',
										'MergedIDLBaseFileName': '$(OutDir)$(TargetName).idl',
										'TypeLibraryFile': '$(OutDir)$(TargetName).tbl',
										'TypeLibraryResourceID': '1',
										'EntryPointSymbol': 'wWinMainCRTStartup',
										'SetChecksum': 'false',
										'BaseAddress': '0x400000',
										'RandomizedBaseAddress': 2,
										'FixedBaseAddress': 1,
										'DataExecutionPrevention': 2,
										'TurnOffAssemblyGeneration': 'false',
										'SupportUnloadOfDelayLoadedDLL': 'true',
										'ImportLibrary': 'dummyG',
										'MergeSections': '.rdata=.text',
										'Profile': 'false',
										'CLRThreadAttribute': 0,
										'CLRImageType': 0,
										'KeyContainer': 'dummyH',
										'CLRUnmanagedCodeCheck': 'false',
										'ErrorReporting': 1,
									},
								},
								'msbuild_props': [
									'../common.props',
								],
							},
							'Release': {
								'msvs_settings': {
									'VCCLCompilerTool': {
										'WholeProgramOptimization': 'true',
										'Optimization': 2,
										'PreprocessorDefinitions': [
											'WIN32',
											'NDEBUG',
											'_WINDOWS',
											'%(PreprocessorDefinitions)',
										],
										'RuntimeLibrary': 0,
										'FloatingPointModel': 2,
										'InlineFunctionExpansion': 2,
										'EnableIntrinsicFunctions': 'true',
										'FavorSizeOrSpeed': 1,
										'OmitFramePointers': 'true',
										'EnableFiberSafeOptimizations': 'true',
										'ExceptionHandling': 1,
										'EnableFunctionLevelLinking': 'true',
										'EnableEnhancedInstructionSet': 2,
									},
									'VCLinkerTool': {
										'GenerateDebugInformation': 'false',
										'LinkIncremental': 1,
										'EnableCOMDATFolding': 2,
										'OptimizeReferences': 2,
										'AdditionalDependencies': [
											'winmm.lib',
											'%(AdditionalDependencies)',
										],
										'LinkTimeCodeGeneration': 3,
									},
								},
							},
						},
						'msvs_settings': {
							'VCLinkerTool': {
								'SubSystem': 2,
								'Version': '3.14159',
								'AdditionalLibraryDirectories': [
									'..\depend\$(Configuration)',
									'%(AdditionalLibraryDirectories)',
								],
								'TargetMachine': 1,
							},
							'VCCLCompilerTool': {
								'UsePrecompiledHeader': 2,
								'WarningLevel': 3,
								'ForcedIncludeFiles': [
									'stdafx.h',
								],
								'OpenMP': 'true',
								'PrecompiledHeaderThrough': 'stdafx.h',
							}
						},
						'msvs_precompiled_source': 'stdafx.cpp',
						'msbuild_toolset': 'v110',
						'msvs_configuration_attributes': {
							'CharacterSet': 1,
						},
						'include_dirs': [
							'../depend',
						],
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
								'msbuild_props': [
									'../common.props',
								],
								'msvs_settings': {
									'VCLibrarianTool': {
										'ForceSymbolReferences': [
											'_exported_function',
										],
										'SuppressStartupBanner': 'false',
										'ExportNamedFunctions': [
											'exported_function_1',
											'exported_function_2',
										],
										'IgnoreSpecificDefaultLibraries': [
											'libcmtd.lib',
										],
									},
								},
							},
							'Release': {
							},
						},
						'msvs_settings': {
							'VCLibrarianTool': {
								'ModuleDefinitionFile': 'depend.def',
								'OutputFile': '$(OutDir)lib\$(ProjectName)$(TargetExt)',
							},
						},
					}
				]
			}
			actual_contents = json.loads(open(expected_depend_gyp_path).read())
			self.assertEqual(expected_contents, actual_contents)
		assert_depend_proj()
