import unittest
import xml.dom.minidom
import sln2gyp

class UtilTestCase(unittest.TestCase):
	def test_xml2obj(self):
		text = '<a><b>value_b</b><c><d>value_d</d></c></a>'
		dom = xml.dom.minidom.parseString(text)
		actual = sln2gyp.xml2obj(dom)
		expected = {
			'a': {
				'b': 'value_b',
				'c': {
					'd': 'value_d',
				}
			}
		}
		self.assertEqual(expected, actual)
