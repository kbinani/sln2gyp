import re

class MsvsOptionConverter:
	_mapping = {
		'SubSystem': {
			'Windows': 2,
			'Console': 1,
			'Native': 3,
			'EFI Application': 4,
			'EFI Boot Service Driver': 5,
			'EFI ROM': 6,
			'EFI Runtime': 7,
			'POSIX': 0,	#TODO(kbinani): gyp does not support 'POSIX' subsystem type
		},
		'StructMemberAlignment': {
			'Default': 0,
			'1Byte': 1,
			'2Bytes': 2,
			'4Bytes': 3,
			'8Bytes': 4,
			'16Bytes': 5,
		},
		'BasicRuntimeChecks': {
			'Default': 0,
			'StackFrameRuntimeCheck': 1,
			'UninitializedLocalUsageCheck': 2,
			'EnableFastChecks': 3,
		},
		'FavorSizeOrSpeed': {
			'Neither': 0,
			'Speed': 1,
			'Size': 2,
		},
		'FloatingPointModel': {
			'Precise': 0,
			'Strict': 1,
			'Fast': 2,
		},
		'RuntimeLibrary': {
			'MultiThreaded': 0,
			'MultiThreadedDebug': 1,
			'MultiThreadedDLL': 2,
			'MultiThreadedDebugDLL': 3,
		},
		'PrecompiledHeader': {
			'Use': 2,
			'Create': 1,
			'NotUsing': 0,
		},
		'DebugInformationFormat': {
			'ProgramDatabase': 3,
			'OldStyle': 1,
			'EditAndContinue': 4,
		},
		'Optimization': {
			'Disabled': 0,
			'MinSpace': 1,
			'MaxSpeed': 2,
			'Full': 3,
		},
		'ExceptionHandling': {
			'false': 0,
			'Async': 2,
			'Sync': 1,
			'SyncCThrow': None, # gyp does not have equivalent value for 'SyncCThrow'
		},
		'InlineFunctionExpansion': {
			'Disabled': None, # gyp does not have equivalent value for 'Disabled'
			'OnlyExplicitInline': 1,
			'AnySuitable': 2,
		},
		'CharacterSet': {
			'Unicode': 1,
			'MultiByte': 2,
		},
		'ConfigurationType': {
			'Application': 'executable',
			'StaticLibrary': 'static_library',
			'DynamicLibrary': 'dynamic_library',
		},
		'EnableEnhancedInstructionSet': {
			'NotSet': 0,
			'StreamingSIMDExtensions': 1,
			'StreamingSIMDExtensions2': 2,
			'AdvancedVectorExtensions': 3,
			'NoExtensions': 4,
        },
		'AssemblerOutput': {
			'NoListing': 0,
			'AssemblyCode': 1,
			'AssemblyAndMachineCode': 3,
			'AssemblyAndSourceCode': 4,
			'All': 2,
		},
	}

	_integer_boolean_msvs_name = {
		'LinkIncremental': None,
		'EnableCOMDATFolding': None,
		'OptimizeReferences': None,
	}

	_string_boolean_msvs_name = {
		'BufferSecurityCheck': None,
		'FunctionLevelLinking': None,
		'FloatingPointExceptions': None,
		'DisableLanguageExtensions': None,
		'TreatWChar_tAsBuiltInType': None,
		'ForceConformanceInForLoopScope': None,
		'RuntimeTypeInfo': None,
		'OpenMPSupport': None,
		'ExpandAttributedSource': None,
		'GenerateXMLDocumentationFiles': None,
	}

	def convert(self, msvs_name, value):
		if msvs_name in self._integer_boolean_msvs_name:
			return self._convert_boolean_to_integer(value)

		if msvs_name in self._string_boolean_msvs_name:
			return self._convert_boolean_to_string(value)

		if msvs_name in self._mapping:
			if value in self._mapping[msvs_name]:
				return self._mapping[msvs_name][value]
			else:
				return None
		else:
			if msvs_name == 'WarningLevel':
				return self._get_warning_level(value)
			else:
				return value

	def _convert_boolean_to_integer(self, boolean_string):
		mapping = {
			'false': 1,
			'true': 2,
		}
		if boolean_string in mapping:
			return mapping[boolean_string];
		else:
			return None

	def _get_warning_level(self, warning_level):
		m = re.compile('Level(?P<level>[0-9]*)').search(warning_level)
		return int(m.group('level'))

	def _convert_boolean_to_string(self, boolean_string):
		if boolean_string == 'true' or boolean_string == 'false':
			return boolean_string
		else:
			return None
