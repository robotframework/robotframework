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

import copy
import os
from collections import OrderedDict
from itertools import chain

from robot.errors import DataError, KeywordError
from robot.libraries import STDLIBS
from robot.output import LOGGER, Message
from robot.utils import (eq, find_file, is_string, normalize, RecommendationFinder,
                         seq2str2)

from .context import EXECUTION_CONTEXTS
from .importer import ImportCache, Importer
from .invalidkeyword import InvalidKeyword
from .resourcemodel import Import
from .runkwregister import RUN_KW_REGISTER


IMPORTER = Importer()


class Namespace:
    _default_libraries = ('BuiltIn', 'Easter')
    _library_import_by_path_ends = ('.py', '/', os.sep)
    _variables_import_by_path_ends = _library_import_by_path_ends + ('.yaml', '.yml') + ('.json',)

    def __init__(self, variables, suite, resource, languages):
        LOGGER.info(f"Initializing namespace for suite '{suite.full_name}'.")
        self.variables = variables
        self.languages = languages
        self._imports = resource.imports
        self._kw_store = KeywordStore(resource, languages)
        self._imported_variable_files = ImportCache()
        self._suite_name = suite.full_name
        self._running_test = False

    @property
    def libraries(self):
        return self._kw_store.libraries.values()

    def handle_imports(self):
        self._import_default_libraries()
        self._handle_imports(self._imports)

    def _import_default_libraries(self):
        for name in self._default_libraries:
            self.import_library(name, notify=name == 'BuiltIn')

    def _handle_imports(self, import_settings):
        for item in import_settings:
            try:
                if not item.name:
                    raise DataError(f'{item.setting_name} setting requires value.')
                self._import(item)
            except DataError as err:
                item.report_error(err.message)

    def _import(self, import_setting):
        action = import_setting.select(self._import_library,
                                       self._import_resource,
                                       self._import_variables)
        action(import_setting)

    def import_resource(self, name, overwrite=True):
        self._import_resource(Import(Import.RESOURCE, name), overwrite=overwrite)

    def _import_resource(self, import_setting, overwrite=False):
        path = self._resolve_name(import_setting)
        self._validate_not_importing_init_file(path)
        if overwrite or path not in self._kw_store.resources:
            resource = IMPORTER.import_resource(path, self.languages)
            self.variables.set_from_variable_section(resource.variables, overwrite)
            self._kw_store.resources[path] = resource
            self._handle_imports(resource.imports)
            LOGGER.imported("Resource", resource.name,
                            importer=str(import_setting.source),
                            source=path)
        else:
            LOGGER.info(f"Resource file '{path}' already imported by "
                        f"suite '{self._suite_name}'.")

    def _validate_not_importing_init_file(self, path):
        name = os.path.splitext(os.path.basename(path))[0]
        if name.lower() == '__init__':
            raise DataError(f"Initialization file '{path}' cannot be imported as "
                            f"a resource file.")

    def import_variables(self, name, args, overwrite=False):
        self._import_variables(Import(Import.VARIABLES, name, args), overwrite)

    def _import_variables(self, import_setting, overwrite=False):
        path = self._resolve_name(import_setting)
        args = self._resolve_args(import_setting)
        if overwrite or (path, args) not in self._imported_variable_files:
            self._imported_variable_files.add((path, args))
            self.variables.set_from_file(path, args, overwrite)
            LOGGER.imported("Variables", os.path.basename(path),
                            args=list(args),
                            importer=str(import_setting.source),
                            source=path)
        else:
            msg = f"Variable file '{path}'"
            if args:
                msg += f" with arguments {seq2str2(args)}"
            LOGGER.info(f"{msg} already imported by suite '{self._suite_name}'.")

    def import_library(self, name, args=(), alias=None, notify=True):
        self._import_library(Import(Import.LIBRARY, name, args, alias), notify=notify)

    def _import_library(self, import_setting, notify=True):
        name = self._resolve_name(import_setting)
        lib = IMPORTER.import_library(name, import_setting.args,
                                      import_setting.alias, self.variables)
        if lib.name in self._kw_store.libraries:
            LOGGER.info(f"Library '{lib.name}' already imported by suite "
                        f"'{self._suite_name}'.")
            return
        if notify:
            LOGGER.imported("Library", lib.name,
                            args=list(import_setting.args),
                            originalname=lib.real_name,
                            importer=str(import_setting.source),
                            source=str(lib.source or ''))
        self._kw_store.libraries[lib.name] = lib
        lib.scope_manager.start_suite()
        if self._running_test:
            lib.scope_manager.start_test()

    def _resolve_name(self, setting):
        name = setting.name
        try:
            name = self.variables.replace_string(name)
        except DataError as err:
            self._raise_replacing_vars_failed(setting, err)
        if self._is_import_by_path(setting.type, name):
            file_type = setting.select('Library', 'Resource file', 'Variable file')
            return find_file(name, setting.directory, file_type=file_type)
        return name

    def _raise_replacing_vars_failed(self, setting, error):
        raise DataError(f"Replacing variables from setting '{setting.setting_name}' "
                        f"failed: {error}")

    def _is_import_by_path(self, import_type, path):
        if import_type == Import.LIBRARY:
            return path.lower().endswith(self._library_import_by_path_ends)
        if import_type == Import.VARIABLES:
            return path.lower().endswith(self._variables_import_by_path_ends)
        return True

    def _resolve_args(self, import_setting):
        try:
            return self.variables.replace_list(import_setting.args)
        except DataError as err:
            self._raise_replacing_vars_failed(import_setting, err)

    def set_search_order(self, new_order):
        old_order = self._kw_store.search_order
        self._kw_store.search_order = new_order
        return old_order

    def start_test(self):
        self._running_test = True
        self.variables.start_test()
        for lib in self.libraries:
            lib.scope_manager.start_test()

    def end_test(self):
        self.variables.end_test()
        for lib in self.libraries:
            lib.scope_manager.end_test()
        self._running_test = True

    def start_suite(self):
        self.variables.start_suite()

    def end_suite(self, suite):
        for lib in self.libraries:
            lib.scope_manager.end_suite()
        if not suite.parent:
            IMPORTER.close_global_library_listeners()
        self.variables.end_suite()

    def start_user_keyword(self):
        self.variables.start_keyword()

    def end_user_keyword(self):
        self.variables.end_keyword()

    def get_library_instance(self, name):
        return self._kw_store.get_library(name).instance

    def get_library_instances(self):
        return dict((name, lib.instance)
                    for name, lib in self._kw_store.libraries.items())

    def reload_library(self, name_or_instance):
        library = self._kw_store.get_library(name_or_instance)
        library.create_keywords()
        return library

    def get_runner(self, name, recommend_on_failure=True):
        try:
            return self._kw_store.get_runner(name, recommend_on_failure)
        except DataError as err:
            return InvalidKeyword(str(name), error=str(err)).create_runner(name)


class KeywordStore:

    def __init__(self, suite_file, languages):
        self.suite_file = suite_file
        self.libraries = OrderedDict()
        self.resources = ImportCache()
        self.search_order = ()
        self.languages = languages

    def get_library(self, name_or_instance):
        if name_or_instance is None:
            raise DataError("Library can not be None.")
        if is_string(name_or_instance):
            return self._get_lib_by_name(name_or_instance)
        return self._get_lib_by_instance(name_or_instance)

    def _get_lib_by_name(self, name):
        if name in self.libraries:
            return self.libraries[name]
        matches = [lib for lib in self.libraries.values() if eq(lib.name, name)]
        if len(matches) == 1:
            return matches[0]
        self._no_library_found(name, multiple=bool(matches))

    def _no_library_found(self, name, multiple=False):
        if multiple:
            raise DataError(f"Multiple libraries matching '{name}' found.")
        raise DataError(f"No library '{name}' found.")

    def _get_lib_by_instance(self, instance):
        for lib in self.libraries.values():
            if lib._instance is instance:
                return lib
        self._no_library_found(instance)

    def get_runner(self, name, recommend=True):
        runner = self._get_runner(name)
        if runner is None:
            self._raise_no_keyword_found(name, recommend)
        return runner

    def _raise_no_keyword_found(self, name, recommend=True):
        if name.strip(': ').upper() == 'FOR':
            raise KeywordError(
                f"Support for the old FOR loop syntax has been removed. "
                f"Replace '{name}' with 'FOR', end the loop with 'END', and "
                f"remove escaping backslashes."
            )
        if name == '\\':
            raise KeywordError(
                "No keyword with name '\\' found. If it is used inside a for "
                "loop, remove escaping backslashes and end the loop with 'END'."
            )
        message = f"No keyword with name '{name}' found."
        if recommend:
            finder = KeywordRecommendationFinder(self.suite_file,
                                                 *self.libraries.values(),
                                                 *self.resources.values())
            raise KeywordError(finder.recommend_similar_keywords(name, message))
        else:
            raise KeywordError(message)

    def _get_runner(self, name):
        if not name:
            raise DataError('Keyword name cannot be empty.')
        if not is_string(name):
            raise DataError('Keyword name must be a string.')
        runner = self._get_runner_from_suite_file(name)
        if not runner and '.' in name:
            runner = self._get_explicit_runner(name)
        if not runner:
            runner = self._get_implicit_runner(name)
        if not runner:
            runner = self._get_bdd_style_runner(name, self.languages.bdd_prefixes)
        return runner

    def _get_bdd_style_runner(self, name, prefixes):
        parts = name.split()
        for index in range(1, len(parts)):
            prefix = ' '.join(parts[:index]).title()
            if prefix in prefixes:
                runner = self._get_runner(' '.join(parts[index:]))
                if runner:
                    runner = copy.copy(runner)
                    runner.name = name
                    return runner
        return None

    def _get_implicit_runner(self, name):
        return (self._get_runner_from_resource_files(name) or
                self._get_runner_from_libraries(name))

    def _get_runner_from_suite_file(self, name):
        keywords = self.suite_file.find_keywords(name)
        if not keywords:
            return None
        if len(keywords) > 1:
            keywords = self._select_best_matches(keywords)
            if len(keywords) > 1:
                self._raise_multiple_keywords_found(keywords, name)
        runner = keywords[0].create_runner(name, self.languages)
        ctx = EXECUTION_CONTEXTS.current
        caller = ctx.user_keywords[-1] if ctx.user_keywords else ctx.test
        if caller and runner.keyword.source != caller.source:
            if self._exists_in_resource_file(name, caller.source):
                message = (
                    f"Keyword '{caller.full_name}' called keyword '{name}' that exists "
                    f"both in the same resource file as the caller and in the suite "
                    f"file using that resource. The keyword in the suite file is used "
                    f"now, but this will change in Robot Framework 8.0."
                )
                runner.pre_run_messages += Message(message, level='WARN'),
        return runner

    def _select_best_matches(self, keywords):
        # "Normal" matches are considered exact and win over embedded matches.
        normal = [kw for kw in keywords if not kw.embedded]
        if normal:
            return normal
        matches = [kw for kw in keywords
                   if not self._is_worse_match_than_others(kw, keywords)]
        return matches or keywords

    def _is_worse_match_than_others(self, candidate, alternatives):
        for other in alternatives:
            if (candidate is not other
                    and self._is_better_match(other, candidate)
                    and not self._is_better_match(candidate, other)):
                return True
        return False

    def _is_better_match(self, candidate, other):
        # Embedded match is considered better than another if the other matches
        # it, but it doesn't match the other.
        return other.matches(candidate.name) and not candidate.matches(other.name)

    def _exists_in_resource_file(self, name, source):
        for resource in self.resources.values():
            if resource.source == source and resource.find_keywords(name):
                return True
        return False

    def _get_runner_from_resource_files(self, name):
        keywords = [kw for resource in self.resources.values()
                    for kw in resource.find_keywords(name)]
        if not keywords:
            return None
        if len(keywords) > 1:
            keywords = self._filter_based_on_search_order(keywords)
            if len(keywords) > 1:
                keywords = self._prioritize_same_file_or_public(keywords)
                if len(keywords) > 1:
                    keywords = self._select_best_matches(keywords)
                    if len(keywords) > 1:
                        self._raise_multiple_keywords_found(keywords, name)
        return keywords[0].create_runner(name, self.languages)

    def _get_runner_from_libraries(self, name):
        keywords = [kw for lib in self.libraries.values()
                    for kw in lib.find_keywords(name)]
        if not keywords:
            return None
        pre_run_message = None
        if len(keywords) > 1:
            keywords = self._filter_based_on_search_order(keywords)
            if len(keywords) > 1:
                keywords = self._select_best_matches(keywords)
                if len(keywords) > 1:
                    keywords, pre_run_message = self._filter_stdlib_handler(keywords)
                    if len(keywords) > 1:
                        self._raise_multiple_keywords_found(keywords, name)
        runner = keywords[0].create_runner(name, self.languages)
        if pre_run_message:
            runner.pre_run_messages += (pre_run_message,)
        return runner

    def _prioritize_same_file_or_public(self, keywords):
        user_keywords = EXECUTION_CONTEXTS.current.user_keywords
        if user_keywords:
            parent_source = user_keywords[-1].source
            matches = [kw for kw in keywords if kw.source == parent_source]
            if matches:
                return matches
        matches = [kw for kw in keywords if not kw.private]
        return matches or keywords

    def _filter_based_on_search_order(self, keywords):
        for name in self.search_order:
            matches = [kw for kw in keywords if eq(name, kw.owner.name)]
            if matches:
                return matches
        return keywords

    def _filter_stdlib_handler(self, keywords):
        warning = None
        if len(keywords) != 2:
            return keywords, warning
        stdlibs_without_remote = STDLIBS - {'Remote'}
        if keywords[0].owner.real_name in stdlibs_without_remote:
            standard, custom = keywords
        elif keywords[1].owner.real_name in stdlibs_without_remote:
            custom, standard = keywords
        else:
            return keywords, warning
        if not RUN_KW_REGISTER.is_run_keyword(custom.owner.real_name, custom.name):
            warning = self._custom_and_standard_keyword_conflict_warning(custom, standard)
        return [custom], warning

    def _custom_and_standard_keyword_conflict_warning(self, custom, standard):
        custom_with_name = standard_with_name = ''
        if custom.owner.name != custom.owner.real_name:
            custom_with_name = f" imported as '{custom.owner.name}'"
        if standard.owner.name != standard.owner.real_name:
            standard_with_name = f" imported as '{standard.owner.name}'"
        return Message(
            f"Keyword '{standard.name}' found both from a custom library "
            f"'{custom.owner.real_name}'{custom_with_name} and a standard library "
            f"'{standard.owner.real_name}'{standard_with_name}. The custom keyword "
            f"is used. To select explicitly, and to get rid of this warning, use "
            f"either '{custom.full_name}' or '{standard.full_name}'.", level='WARN'
        )

    def _get_explicit_runner(self, name):
        kws_and_names = []
        for owner_name, kw_name in self._get_owner_and_kw_names(name):
            for owner in chain(self.libraries.values(), self.resources.values()):
                if eq(owner.name, owner_name):
                    for kw in owner.find_keywords(kw_name):
                        kws_and_names.append((kw, kw_name))
        if not kws_and_names:
            return None
        if len(kws_and_names) == 1:
            kw, kw_name = kws_and_names[0]
        else:
            keywords = [kw for kw, _ in kws_and_names]
            matches = self._select_best_matches(keywords)
            if len(matches) > 1:
                self._raise_multiple_keywords_found(keywords, name, implicit=False)
            kw, kw_name = kws_and_names[keywords.index(matches[0])]
        return kw.create_runner(kw_name, self.languages)

    def _get_owner_and_kw_names(self, full_name):
        tokens = full_name.split('.')
        return [('.'.join(tokens[:index]), '.'.join(tokens[index:]))
                for index in range(1, len(tokens))]

    def _raise_multiple_keywords_found(self, keywords, name, implicit=True):
        if any(kw.embedded for kw in keywords):
            error = f"Multiple keywords matching name '{name}' found"
        else:
            error = f"Multiple keywords with name '{name}' found"
            if implicit:
                error += ". Give the full name of the keyword you want to use"
        names = sorted(kw.full_name for kw in keywords)
        raise KeywordError('\n    '.join([error+':'] + names))


class KeywordRecommendationFinder:

    def __init__(self, *owners):
        self.owners = owners

    def recommend_similar_keywords(self, name, message):
        """Return keyword names similar to `name`."""
        candidates = self._get_candidates(use_full_name='.' in name)
        finder = RecommendationFinder(
            lambda name: normalize(candidates.get(name, name), ignore='_')
        )
        return finder.find_and_format(name, candidates, message,
                                      check_missing_argument_separator=True)

    @staticmethod
    def format_recommendations(message, recommendations):
        return RecommendationFinder().format(message, recommendations)

    def _get_candidates(self, use_full_name=False):
        candidates = {}
        names = sorted((owner.name or '', kw.name)
                       for owner in self.owners for kw in owner.keywords)
        for owner, name in names:
            full_name = f'{owner}.{name}' if owner else name
            candidates[full_name] = full_name if use_full_name else name
        return candidates
