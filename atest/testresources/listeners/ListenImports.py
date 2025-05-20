import os


class ListenImports:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, imports):
        self.imports = open(imports, "w", encoding="UTF-8")

    def library_import(self, name, attrs):
        self._imported("Library", name, attrs)

    def resource_import(self, name, attrs):
        self._imported("Resource", name, attrs)

    def variables_import(self, name, attrs):
        self._imported("Variables", name, attrs)

    def _imported(self, import_type, name, attrs):
        self.imports.write(f"Imported {import_type}\n\tname: {name}\n")
        for key in sorted(attrs):
            self.imports.write(f"\t{key}: {self._pretty(attrs[key])}\n")

    def _pretty(self, entry):
        if isinstance(entry, list):
            return f"[{', '.join(entry)}]"
        if isinstance(entry, str) and os.path.isabs(entry):
            entry = entry.replace(".pyc", ".py")
            tokens = entry.split(os.sep)
            index = -1 if tokens[-1] != "__init__.py" else -2
            return "//" + "/".join(tokens[index:])
        return entry

    def close(self):
        self.imports.close()
