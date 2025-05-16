#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import inspect
import json

try:
    import yaml
except ImportError:
    yaml = None

from robot.errors import DataError
from robot.output import LOGGER
from robot.utils import (
    DotDict, get_error_message, Importer, is_dict_like, is_list_like, type_name
)

from .store import VariableStore


class VariableFileSetter:

    def __init__(self, store: VariableStore):
        self.store = store

    def set(self, path_or_variables, args=None, overwrite=False):
        variables = self._import_if_needed(path_or_variables, args)
        self._set(variables, overwrite)
        return variables

    def _import_if_needed(self, path_or_variables, args=None):
        if not isinstance(path_or_variables, str):
            return path_or_variables
        LOGGER.info(f"Importing variable file '{path_or_variables}' with args {args}.")
        if path_or_variables.lower().endswith((".yaml", ".yml")):
            importer = YamlImporter()
        elif path_or_variables.lower().endswith(".json"):
            importer = JsonImporter()
        else:
            importer = PythonImporter()
        try:
            return importer.import_variables(path_or_variables, args)
        except Exception:
            args = f"with arguments {args} " if args else ""
            msg = get_error_message()
            raise DataError(
                f"Processing variable file '{path_or_variables}' {args}failed: {msg}"
            )

    def _set(self, variables, overwrite=False):
        for name, value in variables:
            self.store.add(name, value, overwrite, decorated=False)


class PythonImporter:

    def import_variables(self, path, args=None):
        importer = Importer("variable file", LOGGER).import_class_or_module
        var_file = importer(path, instantiate_with_args=())
        return self._get_variables(var_file, args)

    def _get_variables(self, var_file, args):
        if hasattr(var_file, "get_variables"):
            variables = self._get_dynamic(var_file.get_variables, args)
        elif hasattr(var_file, "getVariables"):
            variables = self._get_dynamic(var_file.getVariables, args)
        elif not args:
            variables = self._get_static(var_file)
        else:
            raise DataError("Static variable files do not accept arguments.")
        return list(self._decorate_and_validate(variables))

    def _get_dynamic(self, get_variables, args):
        positional, named = self._resolve_arguments(get_variables, args)
        variables = get_variables(*positional, **dict(named))
        if is_dict_like(variables):
            return variables.items()
        raise DataError(
            f"Expected '{get_variables.__name__}' to return "
            f"a dictionary-like value, got {type_name(variables)}."
        )

    def _resolve_arguments(self, get_variables, args):
        from robot.running.arguments import PythonArgumentParser

        spec = PythonArgumentParser("variable file").parse(get_variables)
        return spec.resolve(args)

    def _get_static(self, var_file):
        names = [attr for attr in dir(var_file) if not attr.startswith("_")]
        if hasattr(var_file, "__all__"):
            names = [name for name in names if name in var_file.__all__]
        variables = [(name, getattr(var_file, name)) for name in names]
        if not inspect.ismodule(var_file):
            variables = [(n, v) for n, v in variables if not callable(v)]
        return variables

    def _decorate_and_validate(self, variables):
        for name, value in variables:
            if name.startswith("LIST__"):
                if not is_list_like(value):
                    raise DataError(
                        f"Invalid variable '{name}': Expected a list-like value, "
                        f"got {type_name(value)}."
                    )
                name = name[6:]
                value = list(value)
            elif name.startswith("DICT__"):
                if not is_dict_like(value):
                    raise DataError(
                        f"Invalid variable '{name}': Expected a dictionary-like value, "
                        f"got {type_name(value)}."
                    )
                name = name[6:]
                value = DotDict(value)
            yield name, value


class JsonImporter:

    def import_variables(self, path, args=None):
        if args:
            raise DataError("JSON variable files do not accept arguments.")
        variables = self._import(path)
        return [(name, self._dot_dict(value)) for name, value in variables]

    def _import(self, path):
        with open(path, encoding="UTF-8") as stream:
            variables = json.load(stream)
        if not is_dict_like(variables):
            raise DataError(
                f"JSON variable file must be a mapping, got {type_name(variables)}."
            )
        return variables.items()

    def _dot_dict(self, value):
        if is_dict_like(value):
            return DotDict((k, self._dot_dict(v)) for k, v in value.items())
        if is_list_like(value):
            return [self._dot_dict(v) for v in value]
        return value


class YamlImporter:

    def import_variables(self, path, args=None):
        if args:
            raise DataError("YAML variable files do not accept arguments.")
        variables = self._import(path)
        return [(name, self._dot_dict(value)) for name, value in variables]

    def _import(self, path):
        with open(path, encoding="UTF-8") as stream:
            variables = self._load_yaml(stream)
        if not is_dict_like(variables):
            raise DataError(
                f"YAML variable file must be a mapping, got {type_name(variables)}."
            )
        return variables.items()

    def _load_yaml(self, stream):
        if not yaml:
            raise DataError(
                "Using YAML variable files requires PyYAML module to be installed."
                "Typically you can install it by running `pip install pyyaml`."
            )
        if yaml.__version__.split(".")[0] == "3":
            return yaml.load(stream)
        return yaml.full_load(stream)

    def _dot_dict(self, value):
        if is_dict_like(value):
            return DotDict((k, self._dot_dict(v)) for k, v in value.items())
        if is_list_like(value):
            return [self._dot_dict(v) for v in value]
        return value
