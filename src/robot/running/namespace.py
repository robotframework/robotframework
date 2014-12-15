#  Copyright 2008-2014 Nokia Solutions and Networks
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

import os
import copy

from robot import utils
from robot.errors import DataError
from robot.variables import GLOBAL_VARIABLES, is_scalar_var
from robot.output import LOGGER, Message
from robot.parsing.settings import Library, Variables, Resource

from .usererrorhandler import UserErrorHandler
from .userkeyword import UserLibrary
from .importer import Importer, ImportCache
from .runkwregister import RUN_KW_REGISTER
from .handlers import _XTimesHandler
from .context import EXECUTION_CONTEXTS


STDLIB_NAMES = set(('BuiltIn', 'Collections', 'DateTime', 'Dialogs', 'Easter',
                    'OperatingSystem', 'Process', 'Remote', 'Reserved',
                    'Screenshot', 'String', 'Telnet', 'XML'))
IMPORTER = Importer()


class Namespace:
    _default_libraries = ('BuiltIn', 'Reserved', 'Easter')
    _deprecated_libraries = {'BuiltIn': 'DeprecatedBuiltIn',
                             'OperatingSystem': 'DeprecatedOperatingSystem'}
    _library_import_by_path_endings = ('.py', '.java', '.class', '/', os.sep)

    def __init__(self, suite, variables, parent_variables, user_keywords,
                 imports):
        LOGGER.info("Initializing namespace for test suite '%s'" % suite.longname)
        self.suite = suite
        self.test = None
        self.uk_handlers = []
        self.variables = _VariableScopes(variables, parent_variables)
        self._imports = imports
        self._kw_store = KeywordStore(user_keywords)
        self._imported_variable_files = ImportCache()

    @property
    def libraries(self):
        return self._kw_store.libraries.values()

    def handle_imports(self):
        self._import_default_libraries()
        self._handle_imports(self._imports)

    def _create_variables(self, suite, parent_vars, suite_variables=None):
        if suite_variables is None:
            suite_variables = suite.variables
        return _VariableScopes(suite_variables, parent_vars)

    def _import_default_libraries(self):
        for name in self._default_libraries:
            self.import_library(name)

    def _handle_imports(self, import_settings):
        for item in import_settings:
            try:
                if not item.name:
                    raise DataError('%s setting requires a name' % item.type)
                self._import(item)
            except DataError, err:
                item.report_invalid_syntax(unicode(err))

    def _import(self, import_setting):
        action = {'Library': self._import_library,
                  'Resource': self._import_resource,
                  'Variables': self._import_variables}[import_setting.type]
        action(import_setting)

    def import_resource(self, name, overwrite=True):
        self._import_resource(Resource(None, name), overwrite=overwrite)

    def _import_resource(self, import_setting, overwrite=False):
        path = self._resolve_name(import_setting)
        self._validate_not_importing_init_file(path)
        if overwrite or path not in self._kw_store.resources:
            resource = IMPORTER.import_resource(path)
            self.variables.set_from_variable_table(resource.variable_table,
                                                   overwrite)
            self._kw_store.resources[path] \
                = UserLibrary(resource.keyword_table.keywords, resource.source)
            self._handle_imports(resource.setting_table.imports)
        else:
            LOGGER.info("Resource file '%s' already imported by suite '%s'"
                        % (path, self.suite.longname))

    def _validate_not_importing_init_file(self, path):
        name = os.path.splitext(os.path.basename(path))[0]
        if name.lower() == '__init__':
            raise DataError("Initialization file '%s' cannot be imported as "
                            "a resource file." % path)

    def import_variables(self, name, args, overwrite=False):
        self._import_variables(Variables(None, name, args), overwrite)

    def _import_variables(self, import_setting, overwrite=False):
        path = self._resolve_name(import_setting)
        args = self._resolve_args(import_setting)
        if overwrite or (path, args) not in self._imported_variable_files:
            self._imported_variable_files.add((path,args))
            self.variables.set_from_file(path, args, overwrite)
        else:
            msg = "Variable file '%s'" % path
            if args:
                msg += " with arguments %s" % utils.seq2str2(args)
            LOGGER.info("%s already imported by suite '%s'"
                        % (msg, self.suite.longname))

    def import_library(self, name, args=None, alias=None):
        self._import_library(Library(None, name, args=args, alias=alias))

    def _import_library(self, import_setting):
        name = self._resolve_name(import_setting)
        lib = IMPORTER.import_library(name, import_setting.args,
                                      import_setting.alias, self.variables)
        if lib.name in self._kw_store.libraries:
            LOGGER.info("Test library '%s' already imported by suite '%s'"
                        % (lib.name, self.suite.longname))
            return
        self._kw_store.libraries[lib.name] = lib
        lib.start_suite()
        if self.test:
            lib.start_test()
        self._import_deprecated_standard_libs(lib.name)

    def _resolve_name(self, import_setting):
        name = import_setting.name
        try:
            name = self.variables.replace_string(name)
        except DataError, err:
            self._raise_replacing_vars_failed(import_setting, err)
        return self._get_path(name, import_setting.directory, import_setting.type)

    def _raise_replacing_vars_failed(self, import_setting, err):
        raise DataError("Replacing variables from setting '%s' failed: %s"
                        % (import_setting.type, unicode(err)))

    def _get_path(self, name, basedir, import_type):
        if import_type == 'Library' and not self._is_library_by_path(name):
            return name.replace(' ', '')
        return utils.find_file(name, basedir, file_type=import_type)

    def _is_library_by_path(self, path):
        return path.lower().endswith(self._library_import_by_path_endings)

    def _resolve_args(self, import_setting):
        try:
            return self.variables.replace_list(import_setting.args)
        except DataError, err:
            self._raise_replacing_vars_failed(import_setting, err)

    def _import_deprecated_standard_libs(self, name):
        if name in self._deprecated_libraries:
            self.import_library(self._deprecated_libraries[name])

    def set_search_order(self, new_order):
        old_order = self._kw_store.search_order
        self._kw_store.search_order = new_order
        return old_order

    def start_test(self, test):
        self.test = test
        self.variables.start_test()
        for lib in self.libraries:
            lib.start_test()

    def end_test(self):
        self.test = None
        self.variables.end_test()
        self.uk_handlers = []
        for lib in self.libraries:
            lib.end_test()

    def end_suite(self):
        self.suite = None
        self.variables.end_suite()
        for lib in self.libraries:
            lib.end_suite()

    def start_user_keyword(self, handler):
        self.variables.start_uk()
        self.uk_handlers.append(handler)

    def end_user_keyword(self):
        self.variables.end_uk()
        self.uk_handlers.pop()

    def get_library_instance(self, libname):
        return self._kw_store.get_library(libname).get_instance()

    def get_handler(self, name):
        try:
            handler = self._kw_store.get_handler(name)
        except DataError, err:
            handler = UserErrorHandler(name, unicode(err))
        self._replace_variables_from_user_handlers(handler)
        return handler

    def _replace_variables_from_user_handlers(self, handler):
        if hasattr(handler, 'replace_variables'):
            handler.replace_variables(self.variables)


class KeywordStore(object):

    def __init__(self, user_keywords):
        self.user_keywords = UserLibrary(user_keywords)
        self.libraries = {}
        self.resources = ImportCache()
        self.search_order = ()

    def get_library(self, name):
        try:
            return self.libraries[name.replace(' ', '')]
        except KeyError:
            raise DataError("No library with name '%s' found." % name)

    def get_handler(self, name):
        handler = self._get_handler(name)
        if handler is None:
            self._raise_no_keyword_found(name)
        return handler

    def _raise_no_keyword_found(self, name):
        msg = "No keyword with name '%s' found." % name
        finder = KeywordRecommendationFinder(self.user_keywords,
                                             self.libraries,
                                             self.resources)
        recommendations = finder.recommend_similar_keywords(name)
        msg = finder.format_recommendations(msg, recommendations)
        raise DataError(msg)

    def _get_handler(self, name):
        handler = None
        if not name:
            raise DataError('Keyword name cannot be empty.')
        if not isinstance(name, basestring):
            raise DataError('Keyword name must be a string.')
        if '.' in name:
            handler = self._get_explicit_handler(name)
        if not handler:
            handler = self._get_implicit_handler(name)
        if not handler:
            handler = self._get_bdd_style_handler(name)
        if not handler:
            handler = self._get_x_times_handler(name)
        return handler

    def _get_x_times_handler(self, name):
        if not self._is_old_x_times_syntax(name):
            return None
        return _XTimesHandler(self._get_handler('Repeat Keyword'), name)

    def _is_old_x_times_syntax(self, name):
        if not name.lower().endswith('x'):
            return False
        times = name[:-1].strip()
        if is_scalar_var(times):
            return True
        try:
            int(times)
        except ValueError:
            return False
        else:
            return True

    def _get_bdd_style_handler(self, name):
        for prefix in ['given ', 'when ', 'then ', 'and ', 'but ']:
            if name.lower().startswith(prefix):
                handler = self._get_handler(name[len(prefix):])
                if handler:
                    handler = copy.copy(handler)
                    handler.name = name
                return handler
        return None

    def _get_implicit_handler(self, name):
        for method in [self._get_handler_from_test_case_file_user_keywords,
                       self._get_handler_from_resource_file_user_keywords,
                       self._get_handler_from_library_keywords]:
            handler = method(name)
            if handler:
                return handler
        return None

    def _get_handler_from_test_case_file_user_keywords(self, name):
        if self.user_keywords.has_handler(name):
            return self.user_keywords.get_handler(name)

    def _get_handler_from_resource_file_user_keywords(self, name):
        found = [lib.get_handler(name) for lib in self.resources.values()
                 if lib.has_handler(name)]
        if not found:
            return None
        if len(found) > 1:
            found = self._get_handler_based_on_search_order(found)
        if len(found) == 1:
            return found[0]
        self._raise_multiple_keywords_found(name, found)

    def _get_handler_from_library_keywords(self, name):
        found = [lib.get_handler(name) for lib in self.libraries.values()
                 if lib.has_handler(name)]
        if not found:
            return None
        if len(found) > 1:
            found = self._get_handler_based_on_search_order(found)
        if len(found) == 2:
            found = self._prefer_process_over_operatingsystem(*found)
        if len(found) == 2:
            found = self._filter_stdlib_handler(*found)
        if len(found) == 1:
            return found[0]
        self._raise_multiple_keywords_found(name, found)

    def _get_handler_based_on_search_order(self, handlers):
        for libname in self.search_order:
            for handler in handlers:
                if utils.eq(libname, handler.libname):
                    return [handler]
        return handlers

    def _prefer_process_over_operatingsystem(self, handler1, handler2):
        handlers = {handler1.library.orig_name: handler1,
                    handler2.library.orig_name: handler2}
        if set(handlers) == set(['Process', 'OperatingSystem']):
            return [handlers['Process']]
        return [handler1, handler2]

    def _filter_stdlib_handler(self, handler1, handler2):
        if handler1.library.orig_name in STDLIB_NAMES:
            standard, custom = handler1, handler2
        elif handler2.library.orig_name in STDLIB_NAMES:
            standard, custom = handler2, handler1
        else:
            return [handler1, handler2]
        if not RUN_KW_REGISTER.is_run_keyword(custom.library.orig_name, custom.name):
            self._custom_and_standard_keyword_conflict_warning(custom, standard)
        return [custom]

    def _custom_and_standard_keyword_conflict_warning(self, custom, standard):
        custom_with_name = standard_with_name = ''
        if custom.library.name != custom.library.orig_name:
            custom_with_name = " imported as '%s'" % custom.library.name
        if standard.library.name != standard.library.orig_name:
            standard_with_name = " imported as '%s'" % standard.library.name
        warning = Message("Keyword '%s' found both from a custom test library "
                          "'%s'%s and a standard library '%s'%s. The custom "
                          "keyword is used. To select explicitly, and to get "
                          "rid of this warning, use either '%s' or '%s'."
                          % (standard.name,
                             custom.library.orig_name, custom_with_name,
                             standard.library.orig_name, standard_with_name,
                             custom.longname, standard.longname), level='WARN')
        if custom.pre_run_messages:
            custom.pre_run_messages.append(warning)
        else:
            custom.pre_run_messages = [warning]

    def _get_explicit_handler(self, name):
        found = []
        for owner_name, kw_name in self._yield_owner_and_kw_names(name):
            found.extend(self._find_keywords(owner_name, kw_name))
        if len(found) > 1:
            self._raise_multiple_keywords_found(name, found, implicit=False)
        return found[0] if found else None

    def _yield_owner_and_kw_names(self, full_name):
        tokens = full_name.split('.')
        for i in range(1, len(tokens)):
            yield '.'.join(tokens[:i]), '.'.join(tokens[i:])

    def _find_keywords(self, owner_name, name):
        return [owner.get_handler(name)
                for owner in self.libraries.values() + self.resources.values()
                if utils.eq(owner.name, owner_name) and owner.has_handler(name)]

    def _raise_multiple_keywords_found(self, name, found, implicit=True):
        error = "Multiple keywords with name '%s' found.\n" % name
        if implicit:
            error += "Give the full name of the keyword you want to use.\n"
        names = sorted(handler.longname for handler in found)
        error += "Found: %s" % utils.seq2str(names)
        raise DataError(error)


class KeywordRecommendationFinder(object):

    def __init__(self, user_keywords, libraries, resources):
        self.user_keywords = user_keywords
        self.libraries = libraries
        self.resources = resources

    def recommend_similar_keywords(self, name):
        """Return keyword names similar to `name`."""
        candidates = self._get_candidates('.' in name)
        normalizer = lambda name: candidates.get(name, name).lower().replace(
            '_', ' ')
        finder = utils.RecommendationFinder(normalizer)
        return finder.find_recommendations(name, candidates)

    @staticmethod
    def format_recommendations(msg, recommendations):
        return utils.RecommendationFinder.format_recommendations(
            msg, recommendations)

    def _get_candidates(self, use_full_name):
        names = {}
        for owner, name in self._get_all_handler_names():
            full_name = '%s.%s' % (owner, name) if owner else name
            names[full_name] = full_name if use_full_name else name
        return names

    def _get_all_handler_names(self):
        """Return a list of (library name, handler name) tuples.

        For user keywords, library name == None.

        Excludes DeprecatedBuiltIn, DeprecatedOperatingSystem,
        and Reserved libraries.
        """
        excluded = ['DeprecatedBuiltIn', 'DeprecatedOperatingSystem',
                    'Reserved']
        handlers = [(None, utils.printable_name(handler_name, True))
                    for handler_name in self.user_keywords.handlers.keys()]
        for library in (self.libraries.values() + self.resources.values()):
            if library.name not in excluded:
                handlers.extend(
                    ((library.name,
                      utils.printable_name(handler_name, code_style=True))
                     for handler_name in library.handlers))
        # sort handlers to ensure consistent ordering between Jython and Python
        return sorted(handlers)


class _VariableScopes:

    def __init__(self, suite_variables, parent_variables):
        # suite and parent are None only when used by copy_all
        if suite_variables is not None:
            suite_variables.update(GLOBAL_VARIABLES)
            self._suite = self.current = suite_variables
        else:
            self._suite = self.current = None
        self._parents = []
        if parent_variables is not None:
            self._parents.append(parent_variables.current)
            self._parents.extend(parent_variables._parents)
        self._test = None
        self._uk_handlers = []

    def __len__(self):
        if self.current:
            return len(self.current)
        return 0

    def copy_all(self):
        vs = _VariableScopes(None, None)
        vs._suite = self._suite
        vs._test = self._test
        vs._uk_handlers = self._uk_handlers[:]
        vs._parents = self._parents[:]
        vs.current = self.current
        return vs

    def replace_list(self, items, replace_until=None):
        return self.current.replace_list(items, replace_until)

    def replace_scalar(self, items):
        return self.current.replace_scalar(items)

    def replace_string(self, string, ignore_errors=False):
        return self.current.replace_string(string, ignore_errors=ignore_errors)

    def set_from_file(self, path, args, overwrite=False):
        variables = self._suite.set_from_file(path, args, overwrite)
        if self._test is not None:
            self._test._set_from_file(variables, overwrite=True)
        for varz in self._uk_handlers:
            varz._set_from_file(variables, overwrite=True)
        if self._uk_handlers:
            self.current._set_from_file(variables, overwrite=True)

    def set_from_variable_table(self, rawvariables, overwrite=False):
        self._suite.set_from_variable_table(rawvariables, overwrite)
        if self._test is not None:
            self._test.set_from_variable_table(rawvariables, overwrite)
        for varz in self._uk_handlers:
            varz.set_from_variable_table(rawvariables, overwrite)
        if self._uk_handlers:
            self.current.set_from_variable_table(rawvariables, overwrite)

    def __getitem__(self, name):
        return self.current[name]

    def __setitem__(self, name, value):
        self.current[name] = value

    def end_suite(self):
        self._suite = self._test = self.current = None

    def start_test(self):
        self._test = self.current = self._suite.copy()

    def end_test(self):
        self.current = self._suite

    def start_uk(self):
        self._uk_handlers.append(self.current)
        self.current = self.current.copy()

    def end_uk(self):
        self.current = self._uk_handlers.pop()

    def set_global(self, name, value):
        GLOBAL_VARIABLES.__setitem__(name, value)
        for ns in EXECUTION_CONTEXTS.namespaces:
            ns.variables.set_suite(name, value)

    def set_suite(self, name, value):
        self._suite.__setitem__(name, value)
        self.set_test(name, value, False)

    def set_test(self, name, value, fail_if_no_test=True):
        if self._test is not None:
            self._test.__setitem__(name, value)
        elif fail_if_no_test:
            raise DataError("Cannot set test variable when no test is started")
        for varz in self._uk_handlers:
            varz.__setitem__(name, value)
        self.current.__setitem__(name, value)

    def keys(self):
        return self.current.keys()

    def has_key(self, key):
        return self.current.has_key(key)

    __contains__ = has_key

    def contains(self, name, extended=False):
        return self.current.contains(name, extended)
