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

from robot import output

from .visitor import ResultVisitor


class MessageFilter(ResultVisitor):

    def __init__(self, level='TRACE'):
        log_level = output.LogLevel(level or 'TRACE')
        self.log_all = log_level.level == 'TRACE'
        self.is_logged = log_level.is_logged


    def start_suite(self, suite):
        if self.log_all:
            return False

    def start_body_item(self, item):
        if hasattr(item, 'body'):
            for msg in item.body.filter(messages=True):
                if not self.is_logged(msg):
                    item.body.remove(msg)
