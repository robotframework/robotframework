#  Copyright 2008-2015 Nokia Solutions and Networks
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

from robot.errors import ExecutionFailed
from robot.model import Tags
from robot.result import Keyword as KeywordResult
from robot.utils import unic

from .arguments import ArgumentSpec
from .statusreporter import StatusReporter


class UserErrorHandler(object):
    """Created if creating handlers fail -- running raises DataError.

    The idea is not to raise DataError at processing time and prevent all
    tests in affected test case file from executing. Instead UserErrorHandler
    is created and if it is ever run DataError is raised then.
    """

    def __init__(self, name, error, libname=None):
        self.name = name
        self.libname = libname
        self.error = unic(error)
        self.arguments = ArgumentSpec()
        self.timeout = ''
        self.tags = Tags()

    @property
    def longname(self):
        return '%s.%s' % (self.libname, self.name) if self.libname else self.name

    @property
    def doc(self):
        return '*Creating keyword failed:* %s' % self.error

    @property
    def shortdoc(self):
        return self.doc.splitlines()[0]

    def create_runner(self, name):
        return self

    def run(self, kw, context):
        result = KeywordResult(kwname=self.name,
                               libname=self.libname,
                               args=kw.args,
                               assign=kw.assign,
                               type=kw.type)
        with StatusReporter(context, result):
            context.fail(self.error)
            raise ExecutionFailed(self.error, syntax=True)

    dry_run = run
