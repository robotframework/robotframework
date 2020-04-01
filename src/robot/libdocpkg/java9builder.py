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

from inspect import cleandoc

from java.nio.charset import StandardCharsets
from java.util import Locale
from javax.lang.model.element.Modifier import PUBLIC
from javax.lang.model.util import ElementFilter
from javax.lang.model.type import TypeKind
from javax.tools import DocumentationTool, ToolProvider

from robot.utils import normalize, printable_name, split_tags_from_doc

from .model import LibraryDoc, KeywordDoc


class JavaDocBuilder(object):

    def build(self, path):
        qualified_name, type_element, fields, constructors, methods, elements \
                = self._get_documentation_data(path)
        libdoc = LibraryDoc(name=qualified_name,
                            doc=self._get_doc(elements, type_element),
                            version=self._get_version(fields),
                            scope=self._get_scope(fields),
                            named_args=False,
                            doc_format=self._get_doc_format(fields),
                            source=path)
        libdoc.inits = self._initializers(elements, constructors)
        libdoc.keywords = self._keywords(elements, methods)
        return libdoc

    def _get_doc(self, elements, element):
        doc = elements.getDocComment(element)
        return cleandoc(doc or '').rstrip()

    def _get_version(self, fields):
        return self._get_attr(fields, 'VERSION')

    def _get_scope(self, fields):
        scope = self._get_attr(fields, 'SCOPE', upper=True)
        return {'GLOBAL': 'GLOBAL',
                'SUITE': 'SUITE',
                'TESTSUITE': 'SUITE'}.get(scope, 'TEST')

    def _get_doc_format(self, fields):
        return self._get_attr(fields, 'DOC_FORMAT', upper=True)

    def _get_attr(self, fields, name, upper=False):
        name = 'ROBOT_LIBRARY_' + name
        for field in fields:
            if field.getSimpleName().toString() == name:
                value = field.getConstantValue()
                if upper:
                    value = normalize(value, ignore='_').upper()
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
        doc, tags = split_tags_from_doc(self._get_doc(elements, method))
        return KeywordDoc(
            name=printable_name(method.getSimpleName().toString(),
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
        param_type = param.asType()
        return (param_type.toString().startswith('java.util.List') or
                (param_type.getKind() == TypeKind.ARRAY and
                 param_type.getComponentType().getKind() != TypeKind.ARRAY))

    def _is_kwargs(self, param):
        return param.asType().toString().startswith('java.util.Map')

    def _get_documentation_data(self, path):
        doc_tool = ToolProvider.getSystemDocumentationTool()
        file_manager = DocumentationTool.getStandardFileManager(
            doc_tool, None, Locale.US, StandardCharsets.UTF_8)
        compiler = ToolProvider.getSystemJavaCompiler()
        source = file_manager.getJavaFileObjectsFromStrings([path])
        task = compiler.getTask(None, None, None, None, None, source)
        type_element = task.analyze().iterator().next()
        elements = task.getElements()
        members = elements.getAllMembers(type_element)
        qf_name = type_element.getQualifiedName().toString()
        fields = [f for f in ElementFilter.fieldsIn(members)
                  if PUBLIC in f.getModifiers()]
        constructors = [c for c in ElementFilter.constructorsIn(members)
                        if PUBLIC in c.getModifiers()]
        methods = [m for m in ElementFilter.methodsIn(members)
                   if m.getEnclosingElement() is type_element and
                   PUBLIC in m.getModifiers()]
        return qf_name, type_element, fields, constructors, methods, elements
