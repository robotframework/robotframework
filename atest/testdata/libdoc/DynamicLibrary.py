import inspect
import os.path


class DynamicLibrary:
    """This doc is overwritten and not shown in docs."""

    ROBOT_LIBRARY_VERSION = 0.1

    def __init__(self, arg1, arg2="These args are shown in docs"):
        """This doc is overwritten and not shown in docs."""

    def get_keyword_names(self):
        return [
            "0",
            "Keyword 1",
            "KW2",
            "no arg spec",
            "Defaults",
            "Keyword-only args",
            "KWO w/ varargs",
            "Embedded ${args} 1",
            "Em${bed}ed ${args} 2",
            "nön-äscii ÜTF-8".encode("UTF-8"),
            "nön-äscii Ünicöde",
            "Tags",
            "Types",
            "Source info",
            "Source path only",
            "Source lineno only",
            "Non-existing source path and lineno",
            "Non-existing source path with lineno",
            "Invalid source info",
        ]

    def run_keyword(self, name, args, kwargs):
        print(name, args)

    def get_keyword_arguments(self, name):
        if name == "Defaults":
            return ["old=style", ("new", "style"), ("cool", True)]
        if name == "Keyword-only args":
            return ["*", "kwo", "another=default"]
        if name == "KWO w/ varargs":
            return ["*varargs", "a", ("b", 2), "c", "**kws"]
        if name == "Types":
            return ["integer", "no type", ("boolean", True)]
        if not name[-1].isdigit():
            return None
        return [f"arg{i + 1}" for i in range(int(name[-1]))]

    def get_keyword_documentation(self, name):
        tags = ""
        if name in ("nön-äscii Ünicöde", "nön-äscii ÜTF-8"):
            kind = "Unicode" if name == "nön-äscii Ünicöde" else "UTF-8"
            doc = f"Hyvää yötä.\n\nСпасибо! ({kind})"
            tags = "\n\nTags: hyvää, yötä"
        elif name.startswith("__"):
            doc = f"Dummy documentation for `{name}`."
        else:
            doc = f"""Dummy documentation for `{name}`.

Neither `Keyword 1` or `KW 2` do anything really interesting.
They do, however, accept some `arguments`.
Neither `introduction` nor `importing` contain any more information.

Examples:
| Keyword 1 | arg |
| KW 2 | arg | arg 2 |
| KW 2 | arg | arg 3 |

-------

http://robotframework.org
"""
        doc = self._add_arg_docs(doc, name) + tags
        if name == "nön-äscii ÜTF-8":
            doc = doc.encode("UTF-8")
        return doc

    def _add_arg_docs(self, doc, name):
        if name == "__intro__":
            return doc
        doc += "\n\nArgs:\n"
        if name == "__init__":
            specs = ["arg1", "arg2=These args are shown in docs"]
        else:
            specs = self.get_keyword_arguments(name) or []
        for spec in specs:
            arg = spec.split("=")[0] if isinstance(spec, str) else spec[0]
            doc += f"    {arg}: Doc for `{arg}`.\n"
        return doc

    def get_keyword_tags(self, name):
        if name == "Tags":
            return ["my", "tägs"]
        return None

    def get_keyword_types(self, name):
        if name == "Types":
            return {"integer": int, "boolean": bool, "return": int}
        return None

    def get_keyword_source(self, name):
        if name == "Source info":
            path = inspect.getsourcefile(type(self))
            lineno = inspect.getsourcelines(self.get_keyword_source)[1]
            return f"{path}:{lineno}"
        if name == "Source path only":
            return os.path.dirname(__file__) + "/Annotations.py"
        if name == "Source lineno only":
            return ":12345"
        if name == "Non-existing source path and lineno":
            return "whatever:xxx"
        if name == "Non-existing source path with lineno":
            return "everwhat:42"
        if name == "Invalid source info":
            return 123
        return None
