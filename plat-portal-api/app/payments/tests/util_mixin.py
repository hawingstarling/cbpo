class AssertComparison(object):
    @classmethod
    def compare(cls, list_compare, _func_compare, _object):
        for ele in list_compare:
            try:
                # instance
                _value_compare = getattr(_object, ele.get("key"))
            except AttributeError:
                # dict
                _value_compare = _object[ele.get("key")]

            _func_compare(
                _value_compare,
                ele.get("value"),
                ele.get("description"),
            )
