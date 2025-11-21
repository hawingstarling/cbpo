from json import JSONEncoder
from uuid import UUID

JSONEncoder_olddefault = JSONEncoder.default


def JSONEncoder_newdefault(self, o):
    if isinstance(o, UUID): return str(o)
    return JSONEncoder_olddefault(self, o)


JSONEncoder.default = JSONEncoder_newdefault
