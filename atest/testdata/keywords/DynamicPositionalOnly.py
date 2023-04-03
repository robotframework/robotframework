class DynamicPositionalOnly:
    kws = {
        "one argument": ["one", "/"],
        "three arguments": ["a", "b", "c", "/"],
        "with normal": ["posonly", "/", "normal"],
        "default str": ["required", "optional=default", "/"],
        "default tuple": ["required", ("optional", "default"), "/"],
        "all args kw": [("one", "value"), "/", ("named", "other"), "*varargs", "**kwargs"],
        "arg with separator": ["/one"],
        "Too many markers": ["one", "/", "two", "/"],
        "After varargs": ["*varargs", "/", "arg"],
        "After named-only marker": ["*", "/", "arg"],
        "After kwargs": ["**kws", "/"],
    }

    def get_keyword_names(self):
        return [key for key in self.kws]

    def run_keyword(self, name, args, kwargs=None):
        if kwargs:
            return f"{name}-{args}-{kwargs}"
        return f"{name}-{args}"

    def get_keyword_arguments(self, name):
        return self.kws[name]
