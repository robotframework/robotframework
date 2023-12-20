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

from pathlib import Path
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from robot import running, result, model


class LoggerApi:

    def start_suite(self, data: 'running.TestSuite', result: 'result.TestSuite'):
        pass

    def end_suite(self, data: 'running.TestSuite', result: 'result.TestSuite'):
        pass

    def start_test(self, data: 'running.TestCase', result: 'result.TestCase'):
        pass

    def end_test(self, data: 'running.TestCase', result: 'result.TestCase'):
        pass

    def start_keyword(self, data: 'running.Keyword', result: 'result.Keyword'):
        self.start_body_item(data, result)

    def end_keyword(self, data: 'running.Keyword', result: 'result.Keyword'):
        self.end_body_item(data, result)

    def start_user_keyword(self, data: 'running.Keyword',
                           implementation: 'running.UserKeyword',
                           result: 'result.Keyword'):
        self.start_keyword(data, result)

    def end_user_keyword(self, data: 'running.Keyword',
                         implementation: 'running.UserKeyword',
                         result: 'result.Keyword'):
        self.end_keyword(data, result)

    def start_library_keyword(self, data: 'running.Keyword',
                              implementation: 'running.LibraryKeyword',
                              result: 'result.Keyword'):
        self.start_keyword(data, result)

    def end_library_keyword(self, data: 'running.Keyword',
                            implementation: 'running.LibraryKeyword',
                            result: 'result.Keyword'):
        self.end_keyword(data, result)

    def start_invalid_keyword(self, data: 'running.Keyword',
                              implementation: 'running.KeywordImplementation',
                              result: 'result.Keyword'):
        self.start_keyword(data, result)

    def end_invalid_keyword(self, data: 'running.Keyword',
                            implementation: 'running.KeywordImplementation',
                            result: 'result.Keyword'):
        self.end_keyword(data, result)

    def start_for(self, data: 'running.For', result: 'result.For'):
        self.start_body_item(data, result)

    def end_for(self, data: 'running.For', result: 'result.For'):
        self.end_body_item(data, result)

    def start_for_iteration(self, data: 'running.ForIteration',
                            result: 'result.ForIteration'):
        self.start_body_item(data, result)

    def end_for_iteration(self, data: 'running.ForIteration',
                          result: 'result.ForIteration'):
        self.end_body_item(data, result)

    def start_while(self, data: 'running.While', result: 'result.While'):
        self.start_body_item(data, result)

    def end_while(self, data: 'running.While', result: 'result.While'):
        self.end_body_item(data, result)

    def start_while_iteration(self, data: 'running.WhileIteration',
                              result: 'result.WhileIteration'):
        self.start_body_item(data, result)

    def end_while_iteration(self, data: 'running.WhileIteration',
                            result: 'result.WhileIteration'):
        self.end_body_item(data, result)

    def start_if(self, data: 'running.If', result: 'result.If'):
        self.start_body_item(data, result)

    def end_if(self, data: 'running.If', result: 'result.If'):
        self.end_body_item(data, result)

    def start_if_branch(self, data: 'running.IfBranch', result: 'result.IfBranch'):
        self.start_body_item(data, result)

    def end_if_branch(self, data: 'running.IfBranch', result: 'result.IfBranch'):
        self.end_body_item(data, result)

    def start_try(self, data: 'running.Try', result: 'result.Try'):
        self.start_body_item(data, result)

    def end_try(self, data: 'running.Try', result: 'result.Try'):
        self.end_body_item(data, result)

    def start_try_branch(self, data: 'running.TryBranch', result: 'result.TryBranch'):
        self.start_body_item(data, result)

    def end_try_branch(self, data: 'running.TryBranch', result: 'result.TryBranch'):
        self.end_body_item(data, result)

    def start_var(self, data: 'running.Var', result: 'result.Var'):
        self.start_body_item(data, result)

    def end_var(self, data: 'running.Var', result: 'result.Var'):
        self.end_body_item(data, result)

    def start_break(self, data: 'running.Break', result: 'result.Break'):
        self.start_body_item(data, result)

    def end_break(self, data: 'running.Break', result: 'result.Break'):
        self.end_body_item(data, result)

    def start_continue(self, data: 'running.Continue', result: 'result.Continue'):
        self.start_body_item(data, result)

    def end_continue(self, data: 'running.Continue', result: 'result.Continue'):
        self.end_body_item(data, result)

    def start_return(self, data: 'running.Return', result: 'result.Return'):
        self.start_body_item(data, result)

    def end_return(self, data: 'running.Return', result: 'result.Return'):
        self.end_body_item(data, result)

    def start_error(self, data: 'running.Error', result: 'result.Error'):
        self.start_body_item(data, result)

    def end_error(self, data: 'running.Error', result: 'result.Error'):
        self.end_body_item(data, result)

    def start_body_item(self, data, result):
        pass

    def end_body_item(self, data, result):
        pass

    def log_message(self, message: 'model.Message'):
        pass

    def message(self, message: 'model.Message'):
        pass

    def output_file(self, path: Path):
        """Called when XML output file is closed.

        Calls :meth:`result_file` by default.
        """
        self.result_file('Output', path)

    def report_file(self, path: Path):
        """Called when report file is closed.

        Calls :meth:`result_file` by default.
        """
        self.result_file('Report', path)

    def log_file(self, path: Path):
        """Called when log file is closed.

        Calls :meth:`result_file` by default.
        """
        self.result_file('Log', path)

    def xunit_file(self, path: Path):
        """Called when xunit file is closed.

        Calls :meth:`result_file` by default.
        """
        self.result_file('XUnit', path)

    def debug_file(self, path: Path):
        """Called when debug file is closed.

        Calls :meth:`result_file` by default.
        """
        self.result_file('Debug', path)

    def result_file(self, kind: Literal['Output', 'Report', 'Log', 'XUnit', 'Debug'],
                    path: Path):
        """Called when any result file is closed by default.

        ``kind`` specifies the file type. This method is not called if a result
        file specific method like :meth:`output_file` is implemented.
        """
        pass

    def imported(self, import_type: str, name: str, attrs):
        pass

    def close(self):
        pass
