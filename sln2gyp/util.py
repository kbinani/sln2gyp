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
		draft = xml_node.nodeValue
		if draft == None:
			return ''
		else:
			return draft

def extract_dict_diff(base, special):
	if base == None or special == None:
		return {}
	obj = {}
	keys = special.keys()
	keys.sort()
	for sp_key in keys:
		if sp_key in base:
			if type(special[sp_key]) != type(base[sp_key]):
				obj[sp_key] = special[sp_key]
			elif isinstance(special[sp_key], dict):
				draft = extract_dict_diff(base[sp_key], special[sp_key])
				if len(draft) > 0:
					obj[sp_key] = draft
			else:
				if special[sp_key] != base[sp_key]:
					obj[sp_key] = special[sp_key]
		else:
			obj[sp_key] = special[sp_key]
	return obj
