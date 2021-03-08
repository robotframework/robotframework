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

    def __init__(self, loglevel=None):
        self.loglevel = loglevel or 'TRACE'

    def start_keyword(self, keyword):
        def is_logged_or_not_message(item):
            return item.type != item.MESSAGE or is_logged(item.level)
        is_logged = IsLogged(self.loglevel)
        keyword.body = keyword.body.filter(predicate=is_logged_or_not_message)
