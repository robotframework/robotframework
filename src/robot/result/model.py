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


class TestSuite(object):

    def __init__(self, parent=None, source='', name='', doc='', status='UNDEFINED'):
        self.parent = parent
        self.source = source
        self.name = name
        self.doc = doc
        self.metadata = {}
        self.status = status
        self.message = ''
        self.keywords = []
        self.suites = []
        self.tests = []
        self.starttime = ''
        self.endtime = ''
        self.elapsedtime = ''

    def create_keyword(self, name):
        keyword = Keyword(name)
        self.keywords.append(keyword)
        return keyword

    def create_test(self, name):
        test = TestCase(self, name)
        self.tests.append(test)
        return test


class TestCase(object):

    def __init__(self, parent=None, name='', doc='', status='UNDEFINED'):
        self.parent = parent
        self.name = name
        self.doc = doc
        self.tags = []
        self.status = status
        self.message = ''
        self.timeout = ''
        self.critical = True
        self.keywords = []
        self.starttime = ''
        self.endtime = ''
        self.elapsedtime = ''

    def create_keyword(self, name):
        keyword = Keyword(name)
        self.keywords.append(keyword)
        return keyword


class Keyword(object):

    def __init__(self, name='', doc='', status='UNDEFINED', type='kw'):
        self.name = name
        self.doc = doc
        self.status = status
        self.type = type
        self.args = []
        self.messages = []
        self.keywords = []
        self.children = []
        self.starttime = ''
        self.endtime = ''
        self.elapsedtime = ''
        self.timeout = ''

    def create_keyword(self, name):
        keyword = Keyword(self, name)
        self.keywords.append(keyword)
        self._add_child(keyword)
        return keyword

    def create_message(self):
        msg = Message()
        self.messages.append(msg)
        self._add_child(msg)
        return msg

    def _add_child(self, child):
        self.children.append(child)


class Message(object):

    def __init__(self, message='', level='INFO', html=False, timestamp='',
                 linkable=False):
        self.message = message
        self.level = level
        self.html = html
        self.timestamp = timestamp
        self.linkable = linkable
