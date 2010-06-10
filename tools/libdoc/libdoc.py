#!/usr/bin/env python

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


"""Robot Framework Library and Resource File Documentation Generator

Usage:  libdoc.py [options] library_or_resource

This script can generate keyword documentation in HTML and XML formats. The
former is suitable for humans and the latter for RIDE, RFDoc, and other tools.
This script can also upload XML documentation to RFDoc system.

Documentation can be created for both test libraries and resource files. All
library and resource file types are supported, and also earlier generated
documentation in XML format can be used as input.

Options:
 -a --argument value *    Possible arguments that a library needs.
 -f --format HTML|XML     Specifies whether to generate HTML or XML output.
                          The default value is got from the output file
                          extension and if the output is not specified the
                          default is HTML.
 -o --output path         Where to write the generated documentation. Can be
                          either a directory or a file, or a URL pointing to
                          RFDoc system's upload page. The default value is the
                          directory where the script is executed from. If
                          a URL is given, it must start with 'http://'.
 -N --name newname        Sets the name of the documented library or resource.
 -T --title title         Sets the title of the generated HTML documentation.
                          Underscores in the given title are automatically
                          converted to spaces.
 -S --styles styles       Overrides the default styles. If the given 'styles'
                          is a path to an existing files, styles will be read
                          from it. If it is string a 'NONE', no styles will be
                          used. Otherwise the given text is used as-is.
 -P --pythonpath path *   Additional path(s) to insert into PYTHONPATH.
 -E --escape what:with *  Escapes characters which are problematic in console.
                          'what' is the name of the character to escape and
                          'with' is the string to escape it with.
                          <-------------------ESCAPES------------------------>
 -h --help                Print this help.

For more information see either the tool's wiki page at
http://code.google.com/p/robotframework/wiki/LibraryDocumentationTool
or tools/libdoc/doc/libdoc.html file inside source distributions.
"""

from __future__ import with_statement
import sys
import os
import re
import tempfile
from httplib import HTTPConnection
from HTMLParser import HTMLParser

from robot.running import TestLibrary, UserLibrary
from robot.serializing import Template, Namespace
from robot.errors import DataError, Information
from robot.parsing import populators
from robot import utils


populators.PROCESS_CURDIR = False


def _uploading(output):
    return output.startswith('http://')


def create_html_doc(lib, outpath, title=None, styles=None):
    if title:
        title = title.replace('_', ' ')
    else:
        title = lib.name
    generated = utils.get_timestamp(daysep='-', millissep=None)
    namespace = Namespace(LIB=lib, TITLE=title, STYLES=_get_styles(styles),
                          GENERATED=generated)
    doc = Template(template=HTML_TEMPLATE).generate(namespace) + '\n'
    outfile = open(outpath, 'w')
    outfile.write(doc.encode('UTF-8'))
    outfile.close()

def _get_styles(styles):
    if not styles:
        return DEFAULT_STYLES
    if styles.upper() == 'NONE':
        return ''
    if os.path.isfile(styles):
        with open(styles) as f:
            return f.read()
    return styles


def create_xml_doc(lib, outpath):
    writer = utils.XmlWriter(outpath)
    writer.start('keywordspec', {'name': lib.name, 'type': lib.type, 'generated': utils.get_timestamp(millissep=None)})
    writer.element('version', lib.version)
    writer.element('scope', lib.scope)
    writer.element('doc', lib.doc)
    _write_keywords_to_xml(writer, 'init', lib.inits)
    _write_keywords_to_xml(writer, 'kw', lib.keywords)
    writer.end('keywordspec')
    writer.close()


def upload_xml_doc(outpath, uploadurl):
    RFDocUploader().upload(outpath, uploadurl)


def _write_keywords_to_xml(writer, kwtype, keywords):
    for kw in keywords:
        attrs = kwtype == 'kw' and {'name': kw.name} or {}
        writer.start(kwtype, attrs)
        writer.element('doc', kw.doc)
        writer.start('arguments')
        for arg in kw.args:
            writer.element('arg', arg)
        writer.end('arguments')
        writer.end(kwtype)


def LibraryDoc(libname, arguments=None, newname=None):
    ext = os.path.splitext(libname)[1].lower()
    if  ext in ('.html', '.htm', '.xhtml', '.tsv', '.txt', '.rst', '.rest'):
        return ResourceDoc(libname, arguments, newname)
    elif ext == '.xml':
        return XmlLibraryDoc(libname, newname)
    elif ext == '.java':
        if not utils.is_jython:
            raise DataError('Documenting Java test libraries requires using Jython.')
        return JavaLibraryDoc(libname, newname)
    else:
        return PythonLibraryDoc(libname, arguments, newname)


class _DocHelper:
    _name_regexp = re.compile("`(.+?)`")
    _list_or_table_regexp = re.compile('^(\d+\.|[-*|]|\[\d+\]) .')

    def __getattr__(self, name):
        if name == 'htmldoc':
            return self._get_htmldoc(self.doc)
        if name == 'htmlshortdoc':
            return utils.html_attr_escape(self.shortdoc)
        if name == 'htmlname':
            return utils.html_attr_escape(self.name)
        raise AttributeError("Non-existing attribute '%s'" % name)

    def _process_doc(self, doc):
        ret = ['']
        for line in doc.splitlines():
            line = line.strip()
            ret.append(self._get_doc_line_separator(line, ret[-1]))
            ret.append(line)
        return ''.join(ret)

    def _get_doc_line_separator(self, line, prev):
        if prev == '':
            return ''
        if line == '':
            return '\n\n'
        if self._list_or_table_regexp.search(line):
            return '\n'
        if prev.startswith('| ') and prev.endswith(' |'):
            return '\n'
        if self.type == 'resource':
            return '\n\n'
        return ' '

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

    def __init__(self, name, arguments=None, newname=None):
        lib = self._import(name, arguments)
        self.supports_named_arguments = lib.supports_named_arguments
        self.name = newname or lib.name
        self.version = utils.html_escape(getattr(lib, 'version', '<unknown>'))
        self.scope = self._get_scope(lib)
        self.doc = self._process_doc(self._get_doc(lib))
        self.inits = self._get_initializers(lib)
        self.keywords = [ KeywordDoc(handler, self)
                          for handler in lib.handlers.values() ]
        self.keywords.sort()

    def _import(self, name, args):
        return TestLibrary(name, args)

    def _get_scope(self, lib):
        if hasattr(lib, 'scope'):
            return {'TESTCASE': 'test case', 'TESTSUITE': 'test suite',
                    'GLOBAL': 'global'}[lib.scope]
        return ''

    def _get_doc(self, lib):
        return lib.doc or "Documentation for test library `%s`." % self.name

    def _get_initializers(self, lib):
        if lib.init.arguments.maxargs == 0:
            return []
        return [KeywordDoc(lib.init, self)]


class ResourceDoc(PythonLibraryDoc):
    type = 'resource'
    supports_named_arguments = True

    def _import(self, path, arguments):
        if arguments:
            raise DataError("Resource file cannot take arguments.")
        return UserLibrary(self._find_resource_file(path))

    def _find_resource_file(self, path):
        if os.path.isfile(path):
            return path
        for dire in [ item for item in sys.path if os.path.isdir(item) ]:
            if os.path.isfile(os.path.join(dire, path)):
                return os.path.join(dire, path)
        raise DataError("Resource file '%s' doesn't exist." % path)

    def _get_doc(self, resource):
        doc = getattr(resource, 'doc', '')  # doc available only in 2.1+
        if not doc:
            doc = "Documentation for resource file `%s`." % self.name
        return utils.unescape(doc)

    def _get_initializers(self, lib):
        return []


class XmlLibraryDoc(_DocHelper):

    def __init__(self, libname, newname):
        dom = utils.DomWrapper(libname)
        self.name = dom.get_attr('name')
        self.type = dom.get_attr('type')
        self.version = dom.get_node('version').text
        self.scope = dom.get_node('scope').text
        self.doc = dom.get_node('doc').text
        self.inits = [ XmlKeywordDoc(node, self) for node in dom.get_nodes('init') ]
        self.keywords = [ XmlKeywordDoc(node, self) for node in dom.get_nodes('kw') ]


class _BaseKeywordDoc(_DocHelper):

    def __init__(self, library):
        self.lib = library
        self.type = library.type

    def __cmp__(self, other):
        return cmp(self.name.lower(), other.name.lower())

    def __getattr__(self, name):
        if name == 'argstr':
            return ', '.join(self.args)
        return _DocHelper.__getattr__(self, name)

    def __repr__(self):
        return "'Keyword %s from library %s'" % (self.name, self.lib.name)


class KeywordDoc(_BaseKeywordDoc):

    def __init__(self, handler, library):
        _BaseKeywordDoc.__init__(self, library)
        self.name = handler.name
        self.args = self._get_args(handler)
        self.doc = self._process_doc(handler.doc)
        self.shortdoc = handler.shortdoc

    def _get_args(self, handler):
        required, defaults, varargs = self._parse_args(handler)
        args = required + [ '%s=%s' % item for item in defaults ]
        if varargs is not None:
            args.append('*%s' % varargs)
        return args

    def _parse_args(self, handler):
        args = [ arg.rstrip('_') for arg in handler.arguments.names ]
        # strip ${} from user keywords (args look more consistent e.g. in IDE)
        if handler.type == 'user':
            args = [ arg[2:-1] for arg in args ]
        default_count = len(handler.arguments.defaults)
        if default_count == 0:
            required = args[:]
            defaults = []
        else:
            required = args[:-default_count]
            defaults = zip(args[-default_count:], list(handler.arguments.defaults))
        varargs = handler.arguments.varargs
        varargs = varargs is not None and varargs.rstrip('_') or varargs
        if handler.type == 'user' and varargs is not None:
            varargs = varargs[2:-1]
        return required, defaults, varargs


class XmlKeywordDoc(_BaseKeywordDoc):

    def __init__(self, node, library):
        _BaseKeywordDoc.__init__(self, library)
        self.name = node.get_attr('name', '')
        self.args = [ arg.text for arg in node.get_nodes('arguments/arg') ]
        self.doc = node.get_node('doc').text
        self.shortdoc = self.doc and self.doc.splitlines()[0] or ''


if utils.is_jython:

    class JavaLibraryDoc(_DocHelper):
        type = 'library'
        supports_named_arguments = False

        def __init__(self, path, newname=None):
            cls = self._get_class(path)
            self.name = newname or cls.qualifiedName()
            self.version = self._get_version(cls)
            self.scope = self._get_scope(cls)
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
            version = self._get_attr(cls, 'VERSION', '<unknown>')
            return utils.html_escape(version)

        def _get_scope(self, cls):
            scope = self._get_attr(cls, 'SCOPE', 'TEST CASE')
            return scope.replace('_', ' ').lower()

        def _get_attr(self, cls, name, default):
            for field in cls.fields():
                if field.name() == 'ROBOT_LIBRARY_' + name \
                        and field.isPublic() and field.constantValue():
                    return field.constantValue()
            return default


    class JavaKeywordDoc(_BaseKeywordDoc):
        # TODO: handle keyword default values and varargs.
        def __init__(self, method, library):
            _BaseKeywordDoc.__init__(self, library)
            self.name = utils.printable_name(method.name(), True)
            self.args = [ param.name() for param in method.parameters() ]
            self.doc = self._process_doc(method.getRawCommentText())
            self.shortdoc = self.doc and self.doc.splitlines()[0] or ''


class RFDocUploader(object):

    def upload(self, file_path, host):
        if host.startswith('http://'):
            host = host[len('http://'):]
        xml_file = open(file_path, 'rb')
        conn = HTTPConnection(host)
        try:
            resp = self._post_multipart(conn, xml_file)
            self._validate_success(resp)
        finally:
            xml_file.close()
            conn.close()

    def _post_multipart(self, conn, xml_file):
        conn.connect()
        content_type, body = self._encode_multipart_formdata(xml_file)
        headers = {'User-Agent': 'libdoc.py', 'Content-Type': content_type}
        conn.request('POST', '/upload/', body, headers)
        return conn.getresponse()

    def _encode_multipart_formdata(self, xml_file):
        boundary = '----------ThIs_Is_tHe_bouNdaRY_$'
        body = """--%(boundary)s
Content-Disposition: form-data; name="override"

on
--%(boundary)s
Content-Disposition: form-data; name="file"; filename="%(filename)s"
Content-Type: text/xml

%(content)s
--%(boundary)s--
""" % {'boundary': boundary, 'filename': xml_file.name, 'content': xml_file.read()}
        content_type = 'multipart/form-data; boundary=%s' % boundary
        return content_type, body.replace('\n', '\r\n')

    def _validate_success(self, resp):
        html = resp.read()
        if resp.status != 200:
            raise DataError(resp.reason.strip())
        if 'Successfully uploaded library' not in html:
            raise DataError('\n'.join(_ErrorParser(html).errors))


class _ErrorParser(HTMLParser):

    def __init__(self, html):
        HTMLParser.__init__(self)
        self._inside_errors = False
        self.errors = []
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attributes):
        if ('class', 'errorlist') in attributes:
            self._inside_errors = True

    def handle_endtag(self, tag):
        if tag == 'ul':
            self._inside_errors = False

    def handle_data(self, data):
        if self._inside_errors and data.strip():
            self.errors.append(data)


DEFAULT_STYLES = '''
<style media="all" type="text/css">
body {
  background: white;
  color: black;
  font-size: small;
  font-family: sans-serif;
  padding: 0.1em 0.5em;
}
a.name, span.name {
  font-style: italic;
}
a, a:link, a:visited {
  color: #c30;
}
a:hover, a:active {
  text-decoration: underline;
  color: black;
}
div.shortcuts {
  margin: 1em 0em;
  font-size: 0.9em;
}
div.shortcuts a {
  text-decoration: none;
  color: black;
}
div.shortcuts a:hover {
  text-decoration: underline;
}
table.keywords {
  border: 2px solid black;
  border-collapse: collapse;
  empty-cells: show;
  margin: 0.3em 0em;
  width: 100%;
}
table.keywords th, table.keywords td {
  border: 2px solid black;
  padding: 0.2em;
  vertical-align: top;
}
table.keywords th {
  background: #bbb;
  color: black;
}
table.keywords td.kw {
  width: 150px;
  font-weight: bold;
}
table.keywords td.arg {
  width: 300px;
  font-style: italic;
}
table.doc {
  border: 1px solid black;
  background: transparent;
  border-collapse: collapse;
  empty-cells: show;
  font-size: 0.85em;
}
table.doc td {
  border: 1px solid black;
  padding: 0.1em 0.3em;
  height: 1.2em;

}
#footer {
  font-size: 0.9em;
}
</style>
<style media="print" type="text/css">
body {
  margin: 0px 1px;
  padding: 0px;
  font-size: 10px;
}
a {
  text-decoration: none;
}
</style>
'''.strip()


HTML_TEMPLATE = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title>${TITLE}</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
${STYLES}
</head>
<body>
<h1>${TITLE}</h1>
<!-- IF "${LIB.version}" != "&lt;unknown&gt;" -->
<b>Version:</b> ${LIB.version}<br>
<!-- END IF -->
<!-- IF "${LIB.type}" == "library" -->
<b>Scope:</b> ${LIB.scope}<br>
<!-- END IF -->
<b>Named arguments: </b>
<!-- IF ${LIB.supports_named_arguments} -->
supported
<!-- ELSE -->
not supported
<!-- END IF -->

<h2 id="introduction">Introduction</h2>
<p>${LIB.htmldoc}</p>

<!-- IF ${LIB.inits} -->
<h2 id="importing">Importing</h2>
<table border="1" class="keywords">
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
<div class='shortcuts'>
<!-- FOR ${kw} IN ${LIB.keywords} -->
<a href="#${kw.htmlname}" title="${kw.htmlshortdoc}">${kw.htmlname.replace(' ','&nbsp;')}</a>
<!-- IF ${kw} != ${LIB.keywords[-1]} -->
&nbsp;&middot;&nbsp;
<!-- END IF -->
<!-- END FOR -->
</div>

<h2>Keywords</h2>
<table border="1" class="keywords">
<tr>
  <th class="kw">Keyword</th>
  <th class="arg">Arguments</th>
  <th class="doc">Documentation</th>
</tr>
<!-- FOR ${kw} IN ${LIB.keywords} -->
<tr>
  <td class="kw"><a name="${kw.htmlname}"></a>${kw.htmlname}</td>
  <td class="arg">${kw.argstr}</td>
  <td class="doc">${kw.htmldoc}</td>
</tr>
<!-- END FOR -->
</table>
<p id="footer">
Altogether ${LIB.keywords.__len__()} keywords.<br />
Generated by <a href="http://code.google.com/p/robotframework/wiki/LibraryDocumentationTool">libdoc.py</a>
on ${GENERATED}.
</p>
</body>
</html>
'''

if __name__ == '__main__':

    def get_format(format, output):
        if format:
            return format.upper()
        if os.path.splitext(output)[1].upper() == '.XML':
            return 'XML'
        return 'HTML'

    def get_unique_path(base, ext, index=0):
        if index == 0:
            path = '%s.%s' % (base, ext)
        else:
            path = '%s-%d.%s' % (base, index, ext)
        if os.path.exists(path):
            return get_unique_path(base, ext, index+1)
        return path


    try:
        argparser = utils.ArgumentParser(__doc__)
        opts, args = argparser.parse_args(sys.argv[1:], pythonpath='pythonpath',
                                          help='help', unescape='escape',
                                          check_args=True)
        libname = args[0]
        library = LibraryDoc(libname, opts['argument'], opts['name'])
        output = opts['output'] or '.'
        if _uploading(output):
            file_path = os.path.join(tempfile.gettempdir(), 'libdoc_upload.xml')
            create_xml_doc(library, file_path)
            upload_xml_doc(file_path, output)
            os.remove(file_path)
        else:
            format = get_format(opts['format'], output)
            if os.path.isdir(output):
                output = get_unique_path(os.path.join(output, library.name), format.lower())
            output = os.path.abspath(output)
            if format == 'HTML':
                create_html_doc(library, output, opts['title'], opts['styles'])
            else:
                create_xml_doc(library, output)
    except Information, msg:
        print msg
    except DataError, err:
        print err, '\n\nTry --help for usage information.'
    except Exception, err:
        print err
    else:
        print '%s -> %s' % (library.name, output)
