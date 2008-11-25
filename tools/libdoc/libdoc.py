#!/usr/bin/env python

#  Copyright 2008 Nokia Siemens Networks Oyj
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


"""Robot Framework Library and Resource File Documentation Generator

Usage:  libdoc.py [options] library_or_resource

This script can generate keyword documentation in HTML or XML. The former is
for humans and the latter mainly for Robot Framework IDE and other tools.
Documentation can be created for both test libraries and resource files.

Options:
 -f --format html|xml    Specifies whether to generate HTML or XML output.
                         The default value is HTML.
 -o --output path        Where to write the generated documentation. If the 
                         path is a directory, the documentation is
                         generated there using the name '<name>.<format>'.
                         If there already is a file with the same name, 
                         an index is added after the '<name>' part. If the
                         path points to a file, it is is used as-is and
                         possible existing file is overwritten. The default
                         value for the path is the directory where the
                         script is executed from.
 -P --pythonpath path *  Additional path(s) to insert into PYTHONPATH.
 -h -? --help            Print this help.

See more information from 'tools/libdoc/doc/libdoc.html folder in case of 
source distribution or from 
http://code.google.com/p/robotframework/wiki/LibraryDocumentationTool 
"""

import sys
import os
import re

from robot.running import TestLibrary, UserLibrary
from robot.serializing import Template, Namespace
from robot import utils
from robot.errors import DataError, Information


def main(args):
    outpath, format, libname = process_arguments(args)
    try:
        library = LibraryDoc(libname)
    except DataError, err:
        exit(error=str(err))
    outpath = get_outpath(outpath, library.name, format)
    if format == 'HTML':
        create_html_doc(library, outpath)
    else:
        create_xml_doc(library, outpath)
    exit(utils.cygpath(outpath))


def process_arguments(args_list):
    argparser = utils.ArgumentParser(__doc__)
    try:
        opts, args = argparser.parse_args(args_list, pythonpath='pythonpath',
                                          help='help', check_args=True)
    except Information, msg:
        exit(msg=str(msg))
    except DataError, err:
        exit(error=str(err))
    output = opts['output'] or '.'
    format = opts['format'] or 'HTML'
    return os.path.abspath(output), format.upper(), args[0]


def get_outpath(path, libname, format):
    if os.path.isdir(path):
        path = os.path.join(path, '%s.%s' % (libname, format.lower()))
        if os.path.exists(path):
            path = get_unique_path(path)
    return path


def get_unique_path(base, index=1):
    body, ext = os.path.splitext(base)
    path = '%s-%d%s' % (body, index, ext)
    if os.path.exists(path):
        path = get_unique_path(base, index+1)
    return path


def create_html_doc(lib, outpath):
    generated = utils.get_timestamp(daysep='-', millissep=None)
    namespace = Namespace(LIB=lib, GENERATED=generated)
    doc = Template(template=DOCUMENT_TEMPLATE).generate(namespace)
    outfile = open(outpath, 'w')
    outfile.write(doc + '\n')
    outfile.close()

    
def create_xml_doc(lib, outpath):
    writer = utils.XmlWriter(outpath)
    writer.start_element('keywordspec', {'name': lib.name, 'type': lib.type,
                                         'generated': utils.get_timestamp(millissep=None)})
    writer.whole_element('doc', lib.doc)
    writer.start_element('keywords')
    for kw in lib.keywords:
        writer.start_element('kw', {'name': kw.name})
        writer.whole_element('doc', kw.doc)
        writer.start_element('arguments')
        for arg in kw.args:
            writer.whole_element('arg', arg)
        writer.end_element('arguments')
        writer.end_element('kw')
    writer.end_element('keywords')
    writer.end_element('keywordspec')
    writer.close()


def exit(msg=None, error=None):
    if msg:
        sys.stdout.write(msg + '\n')
    if error:
        sys.stderr.write(error + '\n\nTry --help for usage information.\n')
        sys.exit(1)
    sys.exit(0)


def LibraryDoc(libname):
    ext = os.path.splitext(libname)[1].lower()
    if  ext in ['.html', '.htm', '.xhtml', '.tsv']:
        return ResourceDoc(libname)
    if ext == '.java':
        if not utils.is_jython:
            exit(error='Documenting Java test libraries requires Jython.')
        return JavaLibraryDoc(libname)
    return PythonLibraryDoc(libname) 


class _DocHelper:

    _name_regexp = re.compile("`(.+?)`")
    _list_or_table_regexp = re.compile('^(\d+\.|[-*|]|\[\d+\]) .')

    def __getattr__(self, name):
        if name == 'htmldoc':
            return self._get_htmldoc(self.doc)
        raise AttributeError("Non-existing attribute '%s'" % name)

    def _process_doc(self, doc):
        ret = ['']
        for line in doc.splitlines():
            line = line.strip()
            if line == '' and ret[-1] != '':
                ret.append('\n\n')
            elif self._list_or_table_regexp.search(line) and ret[-1] != '':
                ret.append('\n')
            elif ret[-1].startswith('| ') and ret[-1].endswith(' |'):
                ret.append('\n')
            elif ret[-1] != '':
                ret.append(' ')
            ret.append(line)
        return ''.join(ret)

    def _get_htmldoc(self, doc):
        doc = utils.html_escape(doc, formatting=True)
        return self._name_regexp.sub(self._link_keywords, doc)

    def _link_keywords(self, res):
        name = res.group(1)
        try:
            lib = self.lib
        except AttributeError:
            lib = self
        for kw in lib.keywords:
            if utils.eq(name, kw.name):
                return '<a href="#%s" class="name">%s</a>' % (kw.name, name)
        if utils.eq_any(name, ['introduction', 'library introduction']):
            return '<a href="#introduction" class="name">%s</a>' % name
        if utils.eq_any(name, ['importing', 'library importing']):
            return '<a href="#importing" class="name">%s</a>' % name
        return '<span class="name">%s</span>' % name


class PythonLibraryDoc(_DocHelper):
    
    type = 'library'
    
    def __init__(self, name):
        lib = self._import(name)
        self.name = lib.name
        self.version = utils.html_escape(getattr(lib, 'version', '<unknown>'))
        self.doc = self._process_doc(self._get_doc(lib))
        self.inits = self._get_initializers(lib)
        self.keywords = [ KeywordDoc(handler, self) 
                          for handler in lib.handlers.values() ]
        self.keywords.sort()

    def _get_initializers(self, lib):
        if not lib.init or lib.init.maxargs == 0:
            return []
        return [KeywordDoc(lib.init, self)]

    def _import(self, name_or_path):
        if os.path.exists(name_or_path):
            parent, name = os.path.split(os.path.normpath(name_or_path))
            sys.path.insert(0, parent)
            name = os.path.splitext(name)[0]
        else:
            name = name_or_path
        return TestLibrary(name)

    def _get_doc(self, lib):
        if lib.doc == '':
            return "Documentation for test library  `%s`." % lib.name
        return lib.doc
    

class ResourceDoc(PythonLibraryDoc):
    
    type = 'resource'
        
    def _import(self, path):
        return UserLibrary(self._find_resource_file(path))

    def _find_resource_file(self, path):
        if os.path.isfile(path):
            return path
        for dire in [ item for item in sys.path if os.path.isdir(item) ]:
            if os.path.isfile(os.path.join(dire, path)):
                return os.path.join(dire, path)
        DataError("Resource file '%s' doesn't exist." % path)
    
    def _get_doc(self, lib):
        return "Documentation for resource file `%s`." % lib.name
    
    def _get_initializers(self, lib):
        return []

    
class _BaseKeywordDoc(_DocHelper):
    
    def __cmp__(self, other):
        return cmp(self.name, other.name)
    
    def __getattr__(self, name):
        if name == 'argstr':
            return ', '.join(self.args)
        return _DocHelper.__getattr__(self, name)

    def __repr__(self):
        return "'Keyword %s from library %s'" % (self.name, self.lib.name)
        

class KeywordDoc(_BaseKeywordDoc):

    def __init__(self, handler, library):
        self.name = handler.name
        self.args = self._get_args(handler) 
        self.doc = self._process_doc(handler.doc)
        self.shortdoc = handler.shortdoc
        self.lib = library

    def _get_args(self, handler):
        required, defaults, varargs = self._parse_args(handler)
        args = required + [ '%s=%s' % item for item in defaults ]
        if varargs is not None:
            args.append('*%s' % varargs)
        return args

    def _parse_args(self, handler):
        args = [ arg.rstrip('_') for arg in handler.args ]
        # strip ${} from user keywords (args look more consistent e.g. in IDE)
        if handler.type == 'user':
            args = [ arg[2:-1] for arg in args ]
        default_count = len(handler.defaults)
        if default_count == 0:
            required = args[:]
            defaults = []
        else:
            required = args[:-default_count]
            defaults = zip(args[-default_count:], list(handler.defaults))
        varargs = handler.varargs
        varargs = varargs is not None and varargs.rstrip('_') or varargs         
        if handler.type == 'user' and varargs is not None:
            varargs = varargs[2:-1]
        return required, defaults, varargs

   
if utils.is_jython:
    
    class JavaLibraryDoc(_DocHelper):
        
        type = 'library'
        
        def __init__(self, path):
            cls = self._get_class(path)
            self.name = cls.qualifiedName()
            self.version = utils.html_escape(self._get_version(cls))
            self.doc = self._process_doc(cls.getRawCommentText())
            self.keywords = [ JavaKeywordDoc(method, self) 
                              for method in cls.methods() ]
            self.inits = [ JavaKeywordDoc(init, self)
                           for init in cls.constructors() ]
            if len(self.inits) == 1 and not self.inits[0].args:
                self.inits = []
            self.keywords.sort()
                            
        def _get_class(self, path):
            """Processes the given Java source file and returns ClassDoc.
            
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
            Messager.preRegister(context, 'libdoc.py')
            jdoctool = JavadocTool.make0(context)
            filter =  ModifierFilter(PUBLIC)
            java_names = List.of(path)
            root = jdoctool.getRootDocImpl('en', 'utf-8', filter, java_names,
                                           List.nil(), False, List.nil(),
                                           List.nil(), False, False, True)
            return root.classes()[0]
        
        def _get_version(self, cls):
            for field in cls.fields():
                if field.name() == 'ROBOT_LIBRARY_VERSION' \
                        and field.isPublic() and field.constantValue():
                    return field.constantValue()
            return '<unknown>'


    class JavaKeywordDoc(_BaseKeywordDoc):
        # TODO: handle keyword default values and varargs.
        def __init__(self, method, library):
            self.name = utils.printable_name(method.name(), True)
            self.args = [ param.name() for param in method.parameters() ]
            self.doc = self._process_doc(method.getRawCommentText())
            self.shortdoc = self.doc and self.doc.splitlines()[0] or ''
            self.lib = library


        
DOCUMENT_TEMPLATE = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>${LIB.name} - Documentation</title>
<style>

  body {
    background: white;
    color: black;
  }

  /* Generic Table Styles */
  table {
    background: white;
    border: 1px solid black;
    border-collapse: collapse;
    empty-cells: show;
    margin: 0.3em 0em;
  }
  th, td {
    border: 1px solid black;
    padding: 0.2em;
  }
  th {
    background: #C6C6C6;
  }
  td {
    vertical-align: top;
  }    

  /* Columns */
  td.kw {
    font-weight: bold;
  }
  td.arg {
    width: 300px;
    font-style: italic;
  }
  td.doc {
  }

  /* Tables in documentation */
  table.doc {
    border: 1px solid gray;
    background: transparent;
    border-collapse: collapse;
    empty-cells: show;
    font-size: 0.85em;
    font-family: arial,helvetica,sans-serif;
  }
  table.doc td {
    border: 1px solid gray;
    padding: 0.1em 0.3em;
    height: 1.2em;
  }

  /* Paragraphs */
  .libdoc, .links {
    width: 800px;
  }

  /* Misc */
  a.name, span.name {  
    font-style: italic;
    background: #f4f4f4;
    text-decoration: none;
  }
  a:link, a:visited {
    color: blue;
  }
  a:hover, a:active {
    text-decoration: underline;
    color: purple;
  }
  .footer {
    font-size: 0.9em;
  }
</style>
</head>
<body>
<h1>${LIB.name} - Documentation</h1>
<!-- IF "${LIB.version}" != "&lt;unknown&gt;" -->
<p><b>Version:</b> ${LIB.version}</p>
<!-- END IF -->

<h2 id="introduction">Introduction</h2>
<p class='libdoc'>${LIB.htmldoc}</p>

<!-- IF ${LIB.inits} -->
<h2 id="importing">Importing</h2>
<table class="keywords">
<tr>
  <th class="arg">Arguments</th>
  <th class="doc">Documentation</th>
</tr>
<!-- FOR ${init} IN ${LIB.inits} -->
<tr>
  <td class="arg">${init.argstr}</td>
  <td class="doc">${init.htmldoc}</td>
</tr>
<!-- END FOR -->
</table>
<!-- END IF -->

<h2>Shortcuts</h2>
<div class='links'>
<!-- FOR ${kw} IN ${LIB.keywords} -->
<a href="#${kw.name}" title="${kw.shortdoc}">${kw.name.replace(' ','&nbsp;')}</a>&nbsp;
<!-- END FOR -->
</div>

<h2>Keywords</h2>
<table class="keywords">
<tr>
  <th class="kw">Keyword</th>
  <th class="arg">Arguments</th>
  <th class="doc">Documentation</th>
</tr>
<!-- FOR ${kw} IN ${LIB.keywords} -->
<tr>
  <td class="kw"><a name="${kw.name}"></a>${kw.name}</td>
  <td class="arg">${kw.argstr}</td>
  <td class="doc">${kw.htmldoc}</td>
</tr>
<!-- END FOR -->
</table>
<p class="footer">
Altogether ${LIB.keywords.__len__()} keywords.<br />
Generated by <a href="http://code.google.com/p/robotframework/wiki/LibraryDocumentationTool">libdoc.py</a>
on ${GENERATED}.
</p>
</body>
</html>
'''

if __name__ == '__main__':
    main(sys.argv[1:])
