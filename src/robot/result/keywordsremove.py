#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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
from robot.result.visitor import Visitor, SkipAllVisitor

def RemoveKeywords(how):
    how = how and how.upper()
    if how == 'PASSED':
        return PassedKeywords(_remove_messages_and_keywords)
    elif how == 'ALL':
        return AllKeywords(_remove_messages_and_keywords)
    else:
        return SkipAllVisitor()

def _remove_messages_and_keywords(item):
    item.messages = []
    item.keywords = []

class AllKeywords(Visitor):

    def __init__(self, action):
        self._action = action

    def start_keyword(self, keyword):
        self._action(keyword)
        return False

class PassedKeywords(Visitor):

    def __init__(self, action):
        self._action = action

    def start_keyword(self, keyword):
        if keyword.status == 'PASS':
            self._action(keyword)

    def start_test(self, test):
        if test.status == 'FAIL':
            return False

