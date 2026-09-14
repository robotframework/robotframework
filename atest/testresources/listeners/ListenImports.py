import os


class ListenImports:
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, imports):
        self.imports = open(imports, "w", encoding="UTF-8")

    def start_library_import(self, importer):
        self._started("Library", importer)

    def start_resource_import(self, importer):
        self._started("Resource", importer)

    def start_variables_import(self, importer):
        self._started("Variables", importer)

    def library_import(self, library, importer):
        self._imported(
            "Library",
            library.name,
            {
                "args": list(importer.args),
                "importer": str(importer.source),
                "originalname": library.real_name,
                "source": str(library.source or ""),
            },
        )

    def resource_import(self, resource, importer):
        self._imported(
            "Resource",
            resource.name,
            {"importer": str(importer.source), "source": str(resource.source)},
        )

    def variables_import(self, attrs, importer):
        self._imported(
            "Variables",
            attrs["name"],
            {
                "args": list(attrs["args"]),
                "importer": str(importer.source),
                "source": str(attrs["source"]),
            },
        )

    def _started(self, import_type, importer):
        self.imports.write(
            f"Started {import_type}\n"
            f"\tname: {self._pretty(importer.name)}\n"
            f"\targs: {self._pretty(list(importer.args))}\n"
        )

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
