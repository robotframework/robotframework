#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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
import re

from robot.common import BaseLibrary, UserErrorHandler
from robot.errors import DataError
from robot.variables import is_list_var, VariableSplitter
from robot import utils

from keywords import Keywords
from timeouts import KeywordTimeout
from arguments import UserKeywordArguments


class UserLibrary(BaseLibrary):
    supports_named_arguments = True # this attribute is for libdoc

    def __init__(self, user_keywords, path=None):
        self.name = self._get_name_for_resource_file(path)
        self.handlers = utils.NormalizedDict(ignore=['_'])
        self.embedded_arg_handlers = []
        for user_keyword in user_keywords:
            try:
                handler = EmbeddedArgsTemplate(user_keyword, self.name)
            except TypeError:
                handler = UserKeywordHandler(user_keyword, self.name)
            else:
                self.embedded_arg_handlers.append(handler)
            if handler.name in self.handlers:
                err = "Keyword '%s' defined multiple times" % handler.name
                handler = UserErrorHandler(handler.name, err)
            self.handlers[handler.name] = handler

    def _get_name_for_resource_file(self, path):
        if path is None:
            return None
        return os.path.splitext(os.path.basename(path))[0]

    def has_handler(self, name):
        if BaseLibrary.has_handler(self, name):
            return True
        for template in self.embedded_arg_handlers:
            try:
                EmbeddedArgs(name, template)
            except TypeError:
                pass
            else:
                return True
        return False

    def get_handler(self, name):
        try:
            return BaseLibrary.get_handler(self, name)
        except DataError, error:
            found = self._get_embedded_arg_handlers(name)
            if not found:
                raise error
            if len(found) == 1:
                return found[0]
            self._raise_multiple_matching_keywords_found(name, found)

    def _get_embedded_arg_handlers(self, name):
        found = []
        for template in self.embedded_arg_handlers:
            try:
                found.append(EmbeddedArgs(name, template))
            except TypeError:
                pass
        return found

    def _raise_multiple_matching_keywords_found(self, name, found):
        names = utils.seq2str([f.origname for f in found])
        if self.name is None:
            where = "Test case file"
        else:
            where = "Resource file '%s'" % self.name
        raise DataError("%s contains multiple keywords matching name '%s'\n"
                        "Found: %s" % (where, name, names))


class UserKeywordHandler(object):
    type = 'user'

    def __init__(self, keyword, libname):
        self.name = keyword.name
        self.keywords = Keywords(keyword.steps)
        self.return_value = keyword.return_.value
        self._libname = libname
        self.doc = self._doc = keyword.doc.value
        self._timeout = keyword.timeout
        self._keyword_args = keyword.args.value

    @property
    def longname(self):
        return '%s.%s' % (self._libname, self.name) if self._libname else self.name

    @property
    def shortdoc(self):
        return self.doc.splitlines()[0] if self.doc else ''

    def init_keyword(self, varz):
        self._errors = []
        self.doc = varz.replace_meta('Documentation', self._doc, self._errors)
        self.timeout = KeywordTimeout(self._timeout.value, self._timeout.message)
        self.timeout.replace_variables(varz)

    def run(self, context, arguments):
        context.namespace.start_user_keyword(self)
        try:
            return self._run(context, arguments)
        finally:
            context.namespace.end_user_keyword()

    def _run(self, context, argument_values):
        args_spec = UserKeywordArguments(self._keyword_args, self.longname)
        variables = context.get_current_vars()
        if context.dry_run:
            return self._dry_run(context, variables, args_spec, argument_values)
        return self._variable_resolving_run(context, variables, args_spec, argument_values)

    def _dry_run(self, context, variables, args_spec, argument_values):
        resolved_arguments = args_spec.resolve_arguments_for_dry_run(argument_values)
        self._execute(context, variables, args_spec, resolved_arguments)
        return None

    def _variable_resolving_run(self, context, variables, args_spec, argument_values):
        resolved_arguments = args_spec.resolve(argument_values, variables)
        self._execute(context, variables, args_spec, resolved_arguments)
        return self._get_return_value(variables)

    def _execute(self, context, variables, args_spec, resolved_arguments):
        args_spec.set_variables(resolved_arguments, variables,
                                     context.output)
        self._verify_keyword_is_valid()
        self.timeout.start()
        self.keywords.run(context)

    def _verify_keyword_is_valid(self):
        if self._errors:
            raise DataError('User keyword initialization failed:\n%s'
                            % '\n'.join(self._errors))
        if not (self.keywords or self.return_value):
            raise DataError("User keyword '%s' contains no keywords"
                            % self.name)

    def _get_return_value(self, variables):
        if not self.return_value:
            return None
        try:
            ret = variables.replace_list(self.return_value)
        except DataError, err:
            raise DataError('Replacing variables from keyword return value '
                            'failed: %s' % unicode(err))
        if len(ret) != 1 or is_list_var(self.return_value[0]):
            return ret
        return ret[0]


class EmbeddedArgsTemplate(UserKeywordHandler):

    def __init__(self, keyword, libname):
        if keyword.args.value:
            raise TypeError('Cannot have normal arguments')
        self.embedded_args, self.name_regexp \
                = self._read_embedded_args_and_regexp(keyword.name)
        if not self.embedded_args:
            raise TypeError('Must have embedded arguments')
        UserKeywordHandler.__init__(self, keyword, libname)

    def _read_embedded_args_and_regexp(self, string):
        args = []
        regexp = ['^']
        while True:
            before, variable, rest = self._split_from_variable(string)
            if before is None:
                break
            args.append(variable)
            regexp.extend([re.escape(before), '(.*?)'])
            string = rest
        regexp.extend([re.escape(rest), '$'])
        return args, re.compile(''.join(regexp), re.IGNORECASE)

    def _split_from_variable(self, string):
        var = VariableSplitter(string, identifiers=['$'])
        if var.identifier is None:
            return None, None, string
        return string[:var.start], string[var.start:var.end], string[var.end:]


class EmbeddedArgs(UserKeywordHandler):

    def __init__(self, name, template):
        match = template.name_regexp.match(name)
        if not match:
            raise TypeError('Does not match given name')
        self.embedded_args = zip(template.embedded_args, match.groups())
        self.name = name
        self.origname = template.name
        self._copy_attrs_from_template(template)

    def run(self, context, args):
        for name, value in self.embedded_args:
            context.get_current_vars()[name] = context.get_current_vars().replace_scalar(value)
        return UserKeywordHandler.run(self, context, args)

    def _copy_attrs_from_template(self, template):
        self._libname = template._libname
        self.keywords = template.keywords
        self._keyword_args = template._keyword_args
        self.return_value = template.return_value
        self.doc = template.doc
        self._doc = template._doc
        self._timeout = template._timeout
