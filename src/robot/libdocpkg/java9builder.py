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

from robot.errors import DataError
from robot import utils

from .model import LibraryDoc, KeywordDoc

try:
    from java.lang import Class
    from java.nio.charset import Charset, StandardCharsets
    from java.util import Locale
    from javax.lang.model.element import Modifier
    from javax.lang.model.util import ElementFilter
    from javax.lang.model.type import TypeKind
    from javax.tools import ToolProvider, DiagnosticListener
except ImportError:
    raise DataError("Can not find JavaDoc related classes.")


class JavaDocBuilder(object):

    def build(self, path):
        qualified_name, type_element, fields, constructors, methods, elements \
            = JavaDocumentation(path)
        libdoc = LibraryDoc(name=qualified_name,
                            doc=self._get_doc(elements, type_element),
                            version=self._get_version(fields),
                            scope=self._get_scope(fields),
                            named_args=False,
                            doc_format=self._get_doc_format(fields))
        libdoc.inits = self._initializers(elements, constructors)
        libdoc.keywords = self._keywords(elements, methods)
        return libdoc

    def _get_doc(self, elements, element):
        doc_comment = elements.getDocComment(element)
        if doc_comment is None:
            return ''
        else:
            return '\n'.join(line.strip() for line in doc_comment.splitlines())

    def _get_version(self, fields):
        return self._get_attr(fields, 'VERSION')

    def _get_scope(self, fields):
        scope = self._get_attr(fields, 'SCOPE', upper=True)
        return {'TESTSUITE': 'test suite',
                'GLOBAL': 'global'}.get(scope, 'test suite')

    def _get_doc_format(self, fields):
        return self._get_attr(fields, 'DOC_FORMAT', upper=True)

    def _get_attr(self, fields, name, upper=False):
        name = 'ROBOT_LIBRARY_' + name
        for field in fields:
            if field.getSimpleName().toString() == name:
                value = field.getConstantValue()
                if upper:
                    value = utils.normalize(value, ignore='_').upper()
                return value
        return ''

    def _initializers(self, elements, constructors):
        inits = [self._keyword_doc(elements, constructor)
                 for constructor in constructors]
        if len(inits) == 1 and not inits[0].args:
            return []
        return inits

    def _keywords(self, elements, methods):
        return [self._keyword_doc(elements, method) for method in methods]

    def _keyword_doc(self, elements, method):
        doc, tags = utils.split_tags_from_doc(self._get_doc(elements, method))
        return KeywordDoc(
            name=utils.printable_name(method.getSimpleName().toString(),
                                      code_style=True),
            args=self._get_keyword_arguments(method),
            doc=doc,
            tags=tags
        )

    def _get_keyword_arguments(self, method):
        params = method.getParameters()
        if not params:
            return []
        names = [param.getSimpleName().toString() for param in params]
        if self._is_varargs(params[-1]):
            names[-1] = '*' + names[-1]
        elif self._is_kwargs(params[-1]):
            names[-1] = '**' + names[-1]
            if len(params) > 1 and self._is_varargs(params[-2]):
                names[-2] = '*' + names[-2]
        return names

    def _is_varargs(self, param):
        return (param.asType().toString().startswith('java.util.List') or
                (param.asType().getKind() == TypeKind.ARRAY and
                 param.asType().getComponentType().getKind() !=
                    TypeKind.ARRAY))

    def _is_kwargs(self, param):
        return param.asType().toString().startswith('java.util.Map')


def JavaDocumentation(path):
    # Need to get the instance with reflection, or we ending up trying to
    # access an internal class not exported.
    doctool = ToolProvider.getSystemDocumentationTool()
    file_manager = Class.forName("javax.tools.DocumentationTool") \
        .getMethod("getStandardFileManager", DiagnosticListener, Locale,
                   Charset) \
        .invoke(doctool, None, Locale.US, StandardCharsets.UTF_8)

    compiler = ToolProvider.getSystemJavaCompiler()
    task = compiler.getTask(None, None, None, None, None,
                            file_manager.getJavaFileObjectsFromStrings([path]))

    type_element = task.analyze().iterator().next()
    elements = task.getElements()
    members = elements.getAllMembers(type_element)
    qf_name = type_element.getQualifiedName().toString()

    fields = filter(lambda field:
                    Modifier.PUBLIC in field.getModifiers(),
                    ElementFilter.fieldsIn(members))

    constructors = filter(lambda constructor:
                          Modifier.PUBLIC in constructor.getModifiers(),
                          ElementFilter.constructorsIn(members))

    methods = filter(lambda member:
                     member.getEnclosingElement() is type_element and
                     Modifier.PUBLIC in member.getModifiers(),
                     ElementFilter.methodsIn(members))

    return qf_name, type_element, fields, constructors, methods, elements
