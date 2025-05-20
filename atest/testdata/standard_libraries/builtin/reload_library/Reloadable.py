from robot.libraries.BuiltIn import BuiltIn
from robot.utils import NormalizedDict

BUILTIN = BuiltIn()

KEYWORDS = NormalizedDict(
    {
        "add_keyword": ("name", "*args"),
        "remove_keyword": ("name",),
        "reload_self": (),
        "original 1": ("arg",),
        "original 2": ("arg",),
        "original 3": ("arg",),
    }
)


class Reloadable:

    def get_keyword_names(self):
        return list(KEYWORDS)

    def get_keyword_arguments(self, name):
        return KEYWORDS[name]

    def get_keyword_documentation(self, name):
        args = ", ".join(KEYWORDS[name])
        return f"Doc for {name} with args {args}"

    def run_keyword(self, name, args):
        print(f"Running keyword '{name}' with arguments {args}.")
        assert name in KEYWORDS
        if name == "add_keyword":
            KEYWORDS[args[0]] = args[1:]
        elif name == "remove_keyword":
            KEYWORDS.pop(args[0])
        elif name == "reload_self":
            BUILTIN.reload_library(self)
        return name
