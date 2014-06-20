import unittest
import sln2gyp

class ConfigurationTest(unittest.TestCase):
	def test_init(self):
		configuration = sln2gyp.Configuration('a', 'b')
		self.assertEqual('a', configuration.configuration())
		self.assertEqual('b', configuration.platform())

	def test_create_from_string(self):
		configuration = sln2gyp.Configuration.create_from_string('c|d')
		self.assertEqual('c', configuration.configuration())
		self.assertEqual('d', configuration.platform())

	def test_is_match(self):
		config = sln2gyp.Configuration('a', 'b')

		self.assertFalse(config.is_match("'$(Configuration)|$(Platform)'=='Debug|Win32'"))
		self.assertTrue(config.is_match("'$(Configuration)|$(Platform)'=='a|b'"))
		self.assertFalse(config.is_match("'$(Configuration)|$(Platform)'=='a|Win32'"))
		self.assertFalse(config.is_match("'$(Configuration)|$(Platform)'=='Debug|b'"))

		self.assertTrue(config.is_match(" '$(Configuration)|$(Platform)' ==    'a|b' "))

		self.assertTrue(config.is_match("'a|b' == '$(Configuration)|$(Platform)'"))

		self.assertTrue(config.is_match("'$(        Configuration )|$(  Platform )'=='a|b'"))

class PropertyTest(unittest.TestCase):
	def test_init(self):
		prop = sln2gyp.Property('A')

		a_b = sln2gyp.Configuration('a', 'b')
		unknown = sln2gyp.Configuration('x', 'y')

		self.assertEqual('A', prop.get(a_b))
		self.assertEqual('A', prop.get(unknown))

		prop.set(a_b, 'B')
		self.assertEqual('B', prop.get(a_b))
		self.assertEqual('A', prop.get(unknown))

		prop.set_default('C')
		self.assertEqual('B', prop.get(a_b))
		self.assertEqual('C', prop.get(unknown))

	def test_get_common_value_for_configurations(self):
		prop = sln2gyp.Property('A')
		a_b = sln2gyp.Configuration('a', 'b')
		c_d = sln2gyp.Configuration('c', 'd')
		unknown = sln2gyp.Configuration('x', 'y')
		prop.set(a_b, 'B')
		prop.set(c_d, 'A')

		configurations = []
		self.assertEqual(None, prop.get_common_value_for_configurations(configurations))

		configurations = [a_b]
		self.assertEqual('B', prop.get_common_value_for_configurations(configurations))

		configurations = [a_b, c_d]
		self.assertEqual(None, prop.get_common_value_for_configurations(configurations))

		configurations = [c_d, unknown]
		self.assertEqual('A', prop.get_common_value_for_configurations(configurations))
