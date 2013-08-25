import hashlib

KNOWN_OPS = '<>+-[].,'


def read_source(file_name):
    with open(file_name, 'r') as f:
        source = f.read()
    return source


def make_hash(s):
    h = hashlib.md5()
    h.update(s)
    return h.hexdigest()

