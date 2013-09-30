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
        from docutils.core import publish_doctree, publish_from_doctree
    except ImportError:
        raise DataError("Using reStructuredText test data requires having "
                        "'docutils' module installed.")

    if not register_custom_directives.registered:
        register_custom_directives()
        register_custom_directives.registered = True

    class RestReader(object):

        def read(self, rstfile, rawdata):
            doctree = publish_doctree(
                rstfile.read(), source_path=rstfile.name,
                settings_overrides={'input_encoding': 'UTF-8'})
            store = RobotDataStorage(doctree)
            if store.has_data():
                return self._read_text(store.get_data(), rawdata)
            return self._read_html(doctree, rawdata)

        def _read_text(self, data, rawdata):
            txtfile = tempfile.NamedTemporaryFile(suffix='.robot')
            txtfile.write(data.encode('UTF-8'))
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

        def _read_html(self, doctree, rawdata):
            htmlfile = tempfile.NamedTemporaryFile(suffix='.html')
            htmlfile.write(publish_from_doctree(
                doctree, writer_name='html',
                settings_overrides={'output_encoding': 'UTF-8'}))
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


def register_custom_directives():
    from docutils.parsers.rst.directives import register_directive
    from docutils.parsers.rst.directives.body import CodeBlock

    class IgnoreCode(CodeBlock):

        def run(self):
            return []

    class CaptureRobotData(CodeBlock):

        def run(self):
            if 'robotframework' in self.arguments:
                store = RobotDataStorage(self.state_machine.document)
                store.add_data(self.content)
            return []

    # 'sourcode' directive is our old custom directive used in User Guide and
    # Quick Start Guide. Should be replaced with the standard 'code' directive.
    register_directive('sourcecode', IgnoreCode)
    register_directive('code', CaptureRobotData)


register_custom_directives.registered = False


class RobotDataStorage(object):

    def __init__(self, document):
        if not hasattr(document, '_robot_data'):
            document._robot_data = []
        self._robot_data = document._robot_data

    def add_data(self, rows):
        self._robot_data.extend(rows)

    def get_data(self):
        return '\n'.join(self._robot_data)

    def has_data(self):
        return bool(self._robot_data)
