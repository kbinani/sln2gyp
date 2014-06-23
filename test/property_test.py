import unittest
import sln2gyp

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
