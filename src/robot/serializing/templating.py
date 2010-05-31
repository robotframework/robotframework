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


import os.path

from robot.variables import Variables
from robot.errors import DataError, FrameworkError
from robot import utils


PRE = '<!-- '
POST = ' -->'


class Namespace(Variables):

    def __init__(self, **kwargs):
        Variables.__init__(self, ['$'])
        for key, value in kwargs.items():
            self['${%s}' % key] = value


class Template:

    def __init__(self, path=None, template=None, functions=None):
        if path is None and template is None:
            raise FrameworkError("Either 'path' or 'template' must be given")
        if template is None:
            tfile = open(path)
            template = tfile.read()
            tfile.close()
            self.parent_dir = os.path.dirname(os.path.abspath(os.path.normpath(path)))
        else:
            self.parent_dir = None
        self._template = template
        self._functions = functions or utils.NormalizedDict()
        # True means handlers for more than single line
        self._handlers = { 'INCLUDE': (self._handle_include, False),
                           'IMPORT': (self._handle_import, False),
                           'CALL': (self._handle_call, False),
                           'IF': (self._handle_if, True),
                           'FOR': (self._handle_for, True),
                           'FUNCTION': (self._handle_function, True) }

    def generate(self, namespace, output=None):
        self._namespace = namespace
        return self._process(self._template, output)

    def _process(self, template, output=None):
        result = Result(output)
        lines = template.splitlines()
        while lines:
            line = lines.pop(0)
            try:
                result.add(self._process_line(line.strip(), lines))
            except ValueError:
                result.add(self._handle_variables(line))
        return result.get_result()

    def _process_line(self, line, lines):
        if not line.startswith(PRE) and line.endswith(POST):
            raise ValueError
        name, expression = line[len(PRE):-len(POST)].split(' ', 1)
        try:
            handler, multiline = self._handlers[name]
        except KeyError:
            raise ValueError
        if multiline:
            block_lines = self._get_multi_line_block(name, lines)
            return handler(expression, block_lines)
        return handler(expression)

    def _get_multi_line_block(self, name, lines):
        """Returns string containing lines before END matching given name.

        Removes the returned lines from given 'lines'.
        """
        block_lines = []
        endline = '%sEND %s%s' % (PRE, name, POST)
        while True:
            try:
                line = lines.pop(0)
            except IndexError:
                raise DataError('Invalid template: No END for %s' % name)
            if line.strip() == endline:
                break
            block_lines.append(line)
        return block_lines

    def _handle_variables(self, template):
        return self._namespace.replace_string(template)

    def _handle_include(self, path):
        included_file = open(self._get_full_path(path))
        include = included_file.read()
        included_file.close()
        return self._handle_variables(include)

    def _handle_import(self, path):
        imported_file = open(self._get_full_path(path))
        self._process(imported_file.read())
        imported_file.close()
        return None

    def _handle_for(self, expression, block_lines):
        block = '\n'.join(block_lines)
        result = []
        var_name, _, value_list = expression.split(' ', 2)
        namespace = self._namespace.copy()
        for value in namespace.replace_scalar(value_list):
            namespace[var_name] = value
            temp = Template(template=block, functions=self._functions)
            ret = temp.generate(namespace)
            if ret:
                result.append(ret)
        if not result:
            return None
        return '\n'.join(result)

    def _handle_if(self, expression, block_lines):
        expression = self._handle_variables(expression)
        if_block, else_block = self._get_if_and_else_blocks(block_lines)
        result = eval(expression) and if_block or else_block
        if not result:
            return None
        return self._process('\n'.join(result))

    def _get_if_and_else_blocks(self, block_lines):
        else_line = PRE + 'ELSE' + POST
        if_block = []
        else_block = []
        block = if_block
        for line in block_lines:
            if line.strip() == else_line:
                block = else_block
            else:
                block.append(line)
        return if_block, else_block

    def _handle_call(self, expression):
        func_tokens = expression.split()
        name = func_tokens[0]
        args = func_tokens[1:]
        namespace = self._namespace.copy()
        try:
            func_args, func_body = self._functions[name]
        except KeyError:
            raise DataError("Non-existing function '%s', available: %s"
                            % (name, self._functions.keys()))
        for key, value in zip(func_args, args):
            namespace[key] = namespace.replace_string(value)
        temp = Template(template=func_body, functions=self._functions)
        return temp.generate(namespace)

    def _handle_function(self, signature, block_lines):
        signature_tokens = signature.split()
        name = signature_tokens[0]
        args = signature_tokens[1:]
        self._functions[name] = (args, '\n'.join(block_lines))

    def _get_full_path(self, path):
        if self.parent_dir is None:
            raise FrameworkError('Parent directory is None. Probably template '
                                 'was string and other files was referred. '
                                 'That is not supported.')
        abs_path = os.path.join(self.parent_dir, path)
        if os.path.exists(abs_path):
            return abs_path
        else:
            raise DataError("File '%s' does not exist." % abs_path)


class Result:

    def __init__(self, output=None):
        self._output = output
        self._result = []

    def add(self, text):
        if text is not None:
            if self._output is None:
                self._result.append(text)
            else:
                self._output.write(text.encode('UTF-8') + '\n')

    def get_result(self):
        if not self._result:
            return None
        return '\n'.join(self._result)
