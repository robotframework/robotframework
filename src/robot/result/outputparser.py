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

from __future__ import with_statement
try:
  from lxml import etree
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
      except ImportError:
        # normal ElementTree install
        import elementtree.ElementTree as etree

from robot.result.elementhandlers import RootHandler
from robot.result.parsingcontext import Context
from robot.result.jsondatamodel import DataModel


class OutputParser(object):

    def __init__(self, log_path='NONE', split_log=False):
        self._context = Context(log_path, split_log)
        self._root_handler = RootHandler(self._context)
        self._handler_stack = [self._root_handler]

    def parse(self, path):
        with open(path, 'r') as outputfile:
            self._parse_fileobj(outputfile)
            return self._get_data_model()

    def _parse_fileobj(self, outputfile):
        for action, elem in etree.iterparse(outputfile, events=('start', 'end')):
            if action == 'start':
                self.startElement(elem.tag, elem.attrib)
            elif action == 'end':
                self.endElement(elem.tag, elem.text or '')

    def _get_data_model(self):
        return DataModel(self._root_handler.data, self._context.split_results)

    def startElement(self, name, attrs):
        self._text = []
        handler = self._handler_stack[-1].get_handler_for(name, attrs)
        self._handler_stack.append(handler)

    def endElement(self, name, text):
        handler = self._handler_stack.pop()
        self._handler_stack[-1].add_child_data(handler.end_element(text))


class CombiningOutputParser(OutputParser):

    def __init__(self,log_path='NONE', split_log=False):
        OutputParser.__init__(self, log_path, split_log)
        self._init_combining_suite()

    def _init_combining_suite(self):
        self.startElement('robot', {'generator':'test'})
        self.startElement('suite', {'name':'Verysimple & Verysimple'})
        self.startElement('doc', {})
        self.endElement('doc', '')
        self.startElement('metadata', {})
        self.endElement('metadata', '')

    def startElement(self, name, attrs):
        OutputParser.startElement(self, name, attrs)

    def endElement(self, name, text):
        handler = self._handler_stack.pop()
        if name == 'robot' and len(self._handler_stack) > 1:
            data = handler._data_from_children[0]
        else:
            data = handler.end_element(text)
        self._handler_stack[-1].add_child_data(data)

    def _get_data_model(self):
        self._close_combining_suite()
        return DataModel(self._root_handler.data, self._context.split_results)

    def _close_combining_suite(self):
        self.startElement('status', {'status':'PASS',
                                     'elapsedtime':"250",
                                     'endtime':"N/A",
                                     'starttime':"N/A"})
        self.endElement('status', '')
        self.endElement('suite', '')
        self.startElement('statistics', {})
        self.endElement('statistics', '')
        self.startElement('errors', {})
        self.endElement('errors', '')
        self.endElement('robot', '')
