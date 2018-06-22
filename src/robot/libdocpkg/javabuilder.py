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

import sys

from robot.errors import DataError
from robot import utils

from .model import LibraryDoc, KeywordDoc


class JavaDocBuilder(object):

    def build(self, path):
        if sys.platform[4:7] < '1.9':
            doc = ClassDoc(path)
        else:
            doc = ClassDocLike(path)
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
        return '\n'.join(line.strip() for line in text.splitlines())

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
                    value = utils.normalize(value, ignore='_').upper()
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
        doc, tags = utils.split_tags_from_doc(self._get_doc(method))
        return KeywordDoc(
            name=utils.printable_name(method.name(), code_style=True),
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
    if sys.platform[4:7] < '1.8':  # API changed in Java 8
        root = jdoctool.getRootDocImpl('en', 'utf-8', filter, java_names,
                                       List.nil(), False, List.nil(),
                                       List.nil(), False, False, True)
    else:
        root = jdoctool.getRootDocImpl('en', 'utf-8', filter, java_names,
                                       List.nil(), List.nil(), False, List.nil(),
                                       List.nil(), False, False, True)
    return root.classes()[0]


def ClassDocLike(path):
    """Process the given Java source file and return an instance that acts like the deprecated ClassDoc. """

    try:
        from javax.tools import ToolProvider, DiagnosticListener
        from java.util import Locale
        from java.nio.charset import Charset, StandardCharsets
        from javax.lang.model.element import Modifier
        from javax.lang.model.type import TypeKind
        from javax.lang.model.util import ElementFilter
        from java.lang import Class
    except ImportError:
        raise DataError("Can not find JavaDoc related classes.")

    class __ClassDocLike(object):
        """ Replacement for deprecated ClassDoc. """

        def __init__(self, qualifiedName, rawCommentText, fields, constructors, methods):
            self.__qualifiedName = qualifiedName
            self.__rawCommentText = rawCommentText
            self.__fields = fields
            self.__constructors = constructors
            self.__methods = methods

        def qualifiedName(self):
            return self.__qualifiedName

        def getRawCommentText(self):
            if self.__rawCommentText is None:
                return ''
            return self.__rawCommentText

        def fields(self):
            return self.__fields

        def constructors(self):
            return self.__constructors

        def methods(self):
            return self.__methods

    class __FieldDocLike(object):
        """ Replacement for deprecated FieldDoc. """

        def __init__(self, name, isPublic, constantValue):
            self.__name = name
            self.__isPublic = isPublic
            self.__constantValue = constantValue

        def name(self):
            return self.__name

        def isPublic(self):
            return self.__isPublic

        def constantValue(self):
            return self.__constantValue

    class __MethodDocLike(object):
        """ Replacement for deprecated ConstructorDoc and MethodDoc classes. """

        def __init__(self, name, rawCommentText, parameters):
            self.__name = name
            self.__rawCommentText = rawCommentText
            self.__parameters = parameters

        def name(self):
            return self.__name

        def getRawCommentText(self):
            if self.__rawCommentText is None:
                return ''
            return self.__rawCommentText

        def parameters(self):
            return self.__parameters

    class __ParameterLike(object):
        """ Replacement for deprecated coms.sun.javadoc.Parameter class. """

        def __init__(self, name, typeName, type):
            self.__name = name
            self.__typeName = typeName
            self.__type = type

        def name(self):
            return self.__name

        def typeName(self):
            return self.__typeName

        def type(self):
            return self.__type

    class __TypeLike(object):
        """ Replacement for deprecated com.sun.javadoc.Type class. """

        def __init__(self, typeMirror):
            self.__typeMirror = typeMirror

        def dimension(self):
            return self.__dimension(self.__typeMirror)

        def __dimension(self, typeMirror):
            if typeMirror.getKind() != TypeKind.ARRAY:
                return ''
            return '[]' + self.__dimension(typeMirror.getComponentType())

    def create_parameters(method):
        return [
            __ParameterLike(
                param.getSimpleName().toString(), param.asType().toString(), __TypeLike(param.asType())
            ) for param in method.getParameters()
        ]

    # Need to get the instance with reflection, or we ending up trying to
    # access an internal class not exported.
    doctool = ToolProvider.getSystemDocumentationTool()
    fileManager = Class.forName("javax.tools.DocumentationTool") \
        .getMethod("getStandardFileManager", DiagnosticListener, Locale, Charset) \
        .invoke(doctool, None, Locale.US, StandardCharsets.UTF_8)

    compiler = ToolProvider.getSystemJavaCompiler()
    task = compiler.getTask(None, None, None, None, None,
                            fileManager.getJavaFileObjectsFromStrings([path]))
    typeElement = task.analyze().iterator().next()
    elements = task.getElements()
    members = elements.getAllMembers(typeElement)

    fields = [
        __FieldDocLike(
            field.getSimpleName().toString(), Modifier.PUBLIC in field.getModifiers(), field.getConstantValue())
        for field in ElementFilter.fieldsIn(members)
    ]
    constructors = [
        __MethodDocLike(
            constructor.getSimpleName().toString(), elements.getDocComment(constructor), create_parameters(constructor))
        for constructor in ElementFilter.constructorsIn(members)
    ]

    declaredMethods = filter(lambda member: member.getEnclosingElement() is typeElement, ElementFilter.methodsIn(members))

    methods = [
        __MethodDocLike(
            method.getSimpleName().toString(), elements.getDocComment(method), create_parameters(method))
        for method in declaredMethods
    ]

    return __ClassDocLike(typeElement.getQualifiedName().toString(),
                          elements.getDocComment(typeElement),
                          fields,
                          constructors,
                          methods)
