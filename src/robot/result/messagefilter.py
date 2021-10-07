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

from robot.output.loggerhelper import IsLogged

from robot.model import SuiteVisitor


class MessageFilter(SuiteVisitor):

    def __init__(self, log_level=None):
        self.is_logged = IsLogged(log_level or 'TRACE')

    def start_suite(self, suite):
        if self.is_logged.level == 'TRACE':
            return False

    def start_keyword(self, keyword):
        for item in list(keyword.body):
            if item.type == item.MESSAGE and not self.is_logged(item.level):
                keyword.body.remove(item)
