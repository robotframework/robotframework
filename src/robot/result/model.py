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

    def __init__(self, parent=None, source='', name='', doc='', status='PASS'):
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


class TestCase(object):

    def __init__(self, parent=None, name='', doc='', status='PASS'):
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


class Keyword(object):

    def __init__(self, name='', doc='', status='PASS', type='kw'):
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
