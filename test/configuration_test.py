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
		self.assertEqual('A', prop.get(a_b))
		prop.set(a_b, 'B')
		self.assertEqual('B', prop.get(a_b))