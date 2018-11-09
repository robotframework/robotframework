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

from robot.errors import DataError
from robot.utils import (JAVA_VERSION, normalize, split_tags_from_doc,
                         printable_name)

from .model import LibraryDoc, KeywordDoc


class JavaDocBuilder(object):

    def build(self, path):
        doc = ClassDoc(path)
        libdoc = LibraryDoc(name=doc.qualifiedName(),
                            doc=self._get_doc(doc),
                            version=self._get_version(doc),
                            scope=self._get_scope(doc),
                            named_args=False,
                            doc_format=self._get_doc_format(doc))
        libdoc.inits = self._initializers(doc)
        libdoc.keywords = self._keywords(doc)
        return libdoc

    def _get_doc(self, doc):
        text = doc.getRawCommentText()
        return cleandoc(text).rstrip()

    def _get_version(self, doc):
        return self._get_attr(doc, 'VERSION')

    def _get_scope(self, doc):
        scope = self._get_attr(doc, 'SCOPE', upper=True)
        return {'TESTSUITE': 'test suite',
                'GLOBAL': 'global'}.get(scope, 'test suite')

    def _get_doc_format(self, doc):
        return self._get_attr(doc, 'DOC_FORMAT', upper=True)

    def _get_attr(self, doc, name, upper=False):
        name = 'ROBOT_LIBRARY_' + name
        for field in doc.fields():
            if field.name() == name and field.isPublic():
                value = field.constantValue()
                if upper:
                    value = normalize(value, ignore='_').upper()
                return value
        return ''

    def _initializers(self, doc):
        inits = [self._keyword_doc(init) for init in doc.constructors()]
        if len(inits) == 1 and not inits[0].args:
            return []
        return inits

    def _keywords(self, doc):
        return [self._keyword_doc(m) for m in doc.methods()]

    def _keyword_doc(self, method):
        doc, tags = split_tags_from_doc(self._get_doc(method))
        return KeywordDoc(
            name=printable_name(method.name(), code_style=True),
            args=self._get_keyword_arguments(method),
            doc=doc,
            tags=tags
        )

    def _get_keyword_arguments(self, method):
        params = method.parameters()
        if not params:
            return []
        names = [p.name() for p in params]
        if self._is_varargs(params[-1]):
            names[-1] = '*' + names[-1]
        elif self._is_kwargs(params[-1]):
            names[-1] = '**' + names[-1]
            if len(params) > 1 and self._is_varargs(params[-2]):
                names[-2] = '*' + names[-2]
        return names

    def _is_varargs(self, param):
        return (param.typeName().startswith('java.util.List')
                or param.type().dimension() == '[]')

    def _is_kwargs(self, param):
        return param.typeName().startswith('java.util.Map')


def ClassDoc(path):
    """Process the given Java source file and return ClassDoc instance.

    Processing is done using com.sun.tools.javadoc APIs. Returned object
    implements com.sun.javadoc.ClassDoc interface:
    http://docs.oracle.com/javase/7/docs/jdk/api/javadoc/doclet/
    """
    try:
        from com.sun.tools.javadoc import JavadocTool, Messager, ModifierFilter
        from com.sun.tools.javac.util import List, Context
        from com.sun.tools.javac.code.Flags import PUBLIC
    except ImportError:
        raise DataError("Creating documentation from Java source files "
                        "requires 'tools.jar' to be in CLASSPATH.")
    context = Context()
    Messager.preRegister(context, 'libdoc')
    jdoctool = JavadocTool.make0(context)
    filter = ModifierFilter(PUBLIC)
    java_names = List.of(path)
    if JAVA_VERSION < (1, 8):  # API changed in Java 8
        root = jdoctool.getRootDocImpl('en', 'utf-8', filter, java_names,
                                       List.nil(), False, List.nil(),
                                       List.nil(), False, False, True)
    else:
        root = jdoctool.getRootDocImpl('en', 'utf-8', filter, java_names,
                                       List.nil(), List.nil(), False, List.nil(),
                                       List.nil(), False, False, True)
    return root.classes()[0]
