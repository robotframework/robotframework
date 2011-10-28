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


class Visitor(object):

    def start_suite(self, suite):
        pass

    def end_suite(self, suite):
        pass

    def start_test(self, test):
        pass

    def end_test(self, test):
        pass

    def start_keyword(self, keyword):
        pass

    def end_keyword(self, keyword):
        pass

    # TODO: Shouldn't we just have message method?
    def log_message(self, msg):
        pass

    # TODO: Stats and errors related methods missing.
    # But do we actually need stat methods?


class TagSetter(Visitor):

    def __init__(self, add=None, remove=None):
        self.add = add
        self.remove = remove

    def start_test(self, test):
        test.tags.add(self.add)
        test.tags.remove(self.remove)
        return False

    def start_keyword(self, keyword):
        return False
