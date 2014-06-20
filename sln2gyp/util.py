import os.path
import xml.dom.minidom

def normpath(path):
	return os.path.normpath(path).replace('\\', '/')

def xml2obj(xml_node):
	if len(xml_node.childNodes) == 1 and xml_node.firstChild.nodeType == xml.dom.Node.TEXT_NODE:
		return xml_node.firstChild.nodeValue
	elif len(xml_node.childNodes) > 0:
		obj = {}
		for node in xml_node.childNodes:
			if node.nodeType != xml.dom.Node.TEXT_NODE:
				name = node.nodeName
				obj[name] = xml2obj(node)
		return obj
	else:
		return xml_node.nodeValue
