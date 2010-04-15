#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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

from keywords import KeywordFactory
from timeouts import KeywordTimeout
from arguments import UserKeywordArguments


def PublicUserLibrary(path):
    """Create a user library instance from given resource file."""
    from robot.parsing import ResourceFile

    resource = ResourceFile(path)
    ret = UserLibrary(resource.user_keywords, path)
    ret.doc = resource.doc
    return ret


class UserLibrary(BaseLibrary):

    def __init__(self, handlerdata, path=None):
        if path is not None:
            self.name = os.path.splitext(os.path.basename(path))[0]
        else:
            self.name = None
        self.handlers = utils.NormalizedDict(ignore=['_'])
        self.embedded_arg_handlers = []
        for handler in handlerdata:
            if handler.type != 'error':
                try:
                    handler = EmbeddedArgsTemplate(handler, self.name)
                except TypeError:
                    handler = UserHandler(handler, self.name)
                else:
                    self.embedded_arg_handlers.append(handler)
            if self.handlers.has_key(handler.name):
                err = "Keyword '%s' defined multiple times" % handler.name
                handler = UserErrorHandler(handler.name, err)
            self.handlers[handler.name] = handler

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


class UserHandler(object):
    type = 'user'
    longname = property(lambda self: not self._libname and self.name
                        or '%s.%s' % (self._libname, self.name))
    shortdoc = property(lambda self: self.doc.splitlines()[0] if self.doc else '')


    def __init__(self, handlerdata, libname):
        self.name = utils.printable_name(handlerdata.name)
        self._libname = libname
        self._set_variable_dependent_metadata(handlerdata.metadata)
        self.keywords = [ KeywordFactory(kw) for kw in handlerdata.keywords ]
        self._arguments = UserKeywordArguments(handlerdata.args,
                                               handlerdata.defaults,
                                               handlerdata.varargs,
                                               handlerdata.minargs,
                                               handlerdata.maxargs,
                                               self.longname)
        self.return_value = handlerdata.return_value

    def _set_variable_dependent_metadata(self, metadata):
        self._doc = metadata.get('Documentation', '')
        self.doc = utils.unescape(self._doc)
        self._timeout = metadata.get('Timeout', [])
        self.timeout = [ utils.unescape(item) for item in self._timeout ]

    def init_user_keyword(self, varz):
        self._errors = []
        self.doc = varz.replace_meta('Documentation', self._doc, self._errors)
        timeout = varz.replace_meta('Timeout', self._timeout, self._errors)
        self.timeout = KeywordTimeout(*timeout)

    def run(self, output, namespace, arguments):
        namespace.start_user_keyword(self)
        try:
            return self._run(output, namespace, arguments)
        finally:
            namespace.end_user_keyword()

    def _run(self, output, namespace, arguments):
        argument_values = self._arguments.resolve(arguments, namespace.variables)
        self._arguments.set_variables(argument_values, namespace.variables,
                                      output)
        self._verify_keyword_is_valid()
        self.timeout.start()
        for kw in self.keywords:
            kw.run(output, namespace)
        return self._get_return_value(namespace.variables)

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
        ret = variables.replace_list(self.return_value)
        if len(ret) != 1 or is_list_var(self.return_value[0]):
            return ret
        return ret[0]


class EmbeddedArgsTemplate(UserHandler):

    def __init__(self, handlerdata, libname):
        if handlerdata.args:
            raise TypeError('Cannot have normal arguments')
        self.embedded_args, self.name_regexp \
                = self._read_embedded_args_and_regexp(handlerdata.name)
        if not self.embedded_args:
            raise TypeError('Must have embedded arguments')
        UserHandler.__init__(self, handlerdata, libname)

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


class EmbeddedArgs(UserHandler):

    def __init__(self, name, template):
        match = template.name_regexp.match(name)
        if not match:
            raise TypeError('Does not match given name')
        self.embedded_args = zip(template.embedded_args, match.groups())
        self.name = name
        self.origname = template.name
        self._copy_attrs_from_template(template)

    def run(self, output, namespace, args):
        for name, value in self.embedded_args:
            namespace.variables[name] = namespace.variables.replace_scalar(value)
        return UserHandler.run(self, output, namespace, args)

    def _copy_attrs_from_template(self, template):
        self._libname = template._libname
        self.keywords = template.keywords
        self._arguments = template._arguments
        self.return_value = template.return_value
        self._doc = template._doc
        self.doc = template.doc
        self._timeout = template._timeout
        self.timeout = template.timeout
