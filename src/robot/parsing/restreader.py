#  Copyright 2008-2013 Nokia Siemens Networks Oyj
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
import tempfile
from robot.errors import DataError
from .htmlreader import HtmlReader
from .txtreader import TxtReader


def RestReader():
    try:
        import docutils.core
        from docutils.parsers.rst.directives import register_directive
        from docutils.parsers.rst.directives import body
    except ImportError:
        raise DataError("Using reStructuredText test data requires having "
                        "'docutils' module installed.")

    # Ignore custom sourcecode directives at least we use in reST sources.
    # See e.g. ug2html.py for an example how custom directives are created.
    ignorer = lambda *args: []
    ignorer.content = 1
    register_directive('sourcecode', ignorer)

    # Override default CodeBlock with a derived custom directive, which can
    # capture Robot Framework test suite snippets and then discard the content
    # to speed up the parser.
    class RobotAwareCodeBlock(body.CodeBlock):
        def run(self):
            if u'robotframework' in self.arguments:
                document = self.state_machine.document
                if RestReader.has_robotdata(document):
                    robotdata = RestReader.get_robotdata(document) + u'\n'
                    robotdata += u'\n'.join(self.content)
                else:
                    robotdata = u'\n'.join(self.content)
                RestReader.set_robotdata(document, robotdata)
            return []  # Parsed content is not required for testing purposes
    register_directive('code', RobotAwareCodeBlock)

    class RestReader:
        def read(self, rstfile, rawdata):
            doctree = docutils.core.publish_doctree(rstfile.read())
            if RestReader.has_robotdata(doctree):
                delegate = RestReader.txtreader_read
            else:
                delegate = RestReader.htmlreader_read
            return delegate(doctree, rawdata)

        @staticmethod
        def has_robotdata(doctree):
            return hasattr(doctree, '_robotdata')

        @staticmethod
        def set_robotdata(doctree, robotdata):
            setattr(doctree, '_robotdata', robotdata)

        @staticmethod
        def get_robotdata(doctree, default=u''):
            return getattr(doctree, '_robotdata', default)

        @staticmethod
        def txtreader_read(doctree, rawdata):
            txtfile = tempfile.NamedTemporaryFile(suffix='.robot')
            txtfile.write(RestReader.get_robotdata(doctree).encode('utf-8'))
            txtfile.seek(0)
            txtreader = TxtReader()
            try:
                return txtreader.read(txtfile, rawdata)
            finally:
                # Ensure that the temp file gets closed and deleted:
                if txtfile:
                    txtfile.close()
                if os.path.isfile(txtfile.name):
                    os.remove(txtfile.name)

        @staticmethod
        def htmlreader_read(doctree, rawdata):
            htmlfile = tempfile.NamedTemporaryFile(suffix='.html')
            htmlfile.write(docutils.core.publish_from_doctree(
                doctree, writer_name='html',
                settings_overrides={'output_encoding': 'utf-8'}))
            htmlfile.seek(0)
            htmlreader = HtmlReader()
            try:
                return htmlreader.read(htmlfile, rawdata)
            finally:
                # Ensure that the temp file gets closed and deleted:
                if htmlfile:
                    htmlfile.close()
                if os.path.isfile(htmlfile.name):
                    os.remove(htmlfile.name)

    return RestReader()
