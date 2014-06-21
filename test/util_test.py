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

	def test_extract_hash_diff(self):
		base = {
			'a': {
				'trivial': 'value_trivial',
				'common': {
					'c': 'value_c',
				}
			},
			'e': {
			}
		}
		special = {
			'a': {
				'trivial': 'value_trivial',
				'common': {
					'c': 'value_c',				
				},
				'special': {
					'd': 'value_d',
				}
			},
			'b': {
				'awsome': 'value_awsome',
			},
			'e': {
				'f': 'value_f',
			}
		}
		actual = sln2gyp.extract_hash_diff(base, special)
		expected = {
			'a': {
				'special': {
					'd': 'value_d',
				}
			},
			'b': {
				'awsome': 'value_awsome',
			},
			'e': {
				'f': 'value_f',
			}
		}
		self.assertEqual(expected, actual)