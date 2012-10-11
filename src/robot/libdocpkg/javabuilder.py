#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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


class JavaDocBuilder(object):

    def build(self, path):
        doc = ClassDoc(path)
        libdoc = LibraryDoc(name=doc.qualifiedName(),
                            doc=self._get_doc(doc),
                            version=self._get_version(doc),
                            scope=self._get_scope(doc),
                            doc_format=self._get_doc_format(doc))
        libdoc.keywords = self._keywords(doc)
        libdoc.inits = self._intializers(doc)
        return libdoc

    def _get_doc(self, doc):
        text = doc.getRawCommentText()
        return '\n'.join(line.strip() for line in text.splitlines())

    def _get_version(self, doc):
        return self._get_attr(doc, 'VERSION')

    def _get_scope(self, doc):
        return self._get_attr(doc, 'SCOPE', default='TESTCASE', upper=True)

    def _get_doc_format(self, doc):
        return self._get_attr(doc, 'DOC_FORMAT', upper=True)

    def _get_attr(self, doc, name, default='', upper=False):
        name = 'ROBOT_LIBRARY_' + name
        for field in doc.fields():
            if field.name() == name and field.isPublic():
                value = field.constantValue()
                if upper:
                    value = utils.normalize(value, ignore='_').upper()
                return value
        return default

    def _keywords(self, doc):
        return [self._keyword_doc(m) for m in doc.methods()]

    def _keyword_doc(self, method):
        return KeywordDoc(
            name=utils.printable_name(method.name(), code_style=True),
            args=list(self._yield_keyword_arguments(method)),
            doc=self._get_doc(method)
        )

    def _yield_keyword_arguments(self, method):
        for param in method.parameters():
            name = param.name()
            if param.type().dimension() == '[]':
                name = '*' + name
            yield name

    def _intializers(self, doc):
        inits = [self._keyword_doc(init) for init in doc.constructors()]
        if len(inits) == 1 and not inits[0].args:
            return []
        return inits


def ClassDoc(path):
    """Process the given Java source file and return ClassDoc instance.

    Processing is done using com.sun.tools.javadoc APIs. The usage has
    been figured out from sources at
    http://www.java2s.com/Open-Source/Java-Document/JDK-Modules-com.sun/tools/com.sun.tools.javadoc.htm

    Returned object implements com.sun.javadoc.ClassDoc interface, see
    http://java.sun.com/j2se/1.4.2/docs/tooldocs/javadoc/doclet/
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
    root = jdoctool.getRootDocImpl('en', 'utf-8', filter, java_names,
                                   List.nil(), False, List.nil(),
                                   List.nil(), False, False, True)
    return root.classes()[0]

