import os.path

def normpath(path):
	return os.path.normpath(path.replace('\\', '/'))
