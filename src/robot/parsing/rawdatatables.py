#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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


from robot import utils
from robot.errors import DataError
from robot.output import LOGGER


_ERR = "Error in file '%s' in table '%s' in element on row %d: %s"


class _Table:
    
    def __init__(self, name, source, data):
        self._name = name
        self._source = source
        self._row = 0
        self._data = data
        
    def add_row(self, cells, repeat=1):
        if len(cells) == 0:
            self._row += repeat
            return
        try:
            for i in range(repeat):
                self._row += 1
                self._add_row(cells[0], cells[1:])
        except:
            self.report_invalid_syntax(self._row, utils.get_error_message())
            
    def report_invalid_syntax(self, row, error, level='ERROR'):
        msg = _ERR % (self._source, self._name, row, error)
        LOGGER.write(msg, level)


class SimpleTable(_Table):
    
    def _add_row(self, name, value):
        if name == '...':
            try:
                self._data[-1].extend(value)
            except IndexError:
                raise DataError('Invalid multirow usage: No item started')
        else:
            item = SimpleItem(name, value, self._row, self)
            self._data.append(item)


class ComplexTable(_Table):

    def __init__(self, name, source, data):
        _Table.__init__(self, name, source, data)
        self._item = None

    def _add_row(self, name, data):
        if name != '':
            self._item = ComplexItem(name, self._row, self)
            self._data.append(self._item)
        if self._item is None:
            raise DataError('No name specified')
        self._item.add_subitem(data)


class _Item:

    def __init__(self, name, row, parent):
        self.name = name
        self._row = row
        self._parent = parent
        
    def report_invalid_syntax(self, error=None, level='ERROR'):
        if error is None:
            error = utils.get_error_message()
        self._parent.report_invalid_syntax(self._row, error, level)


class SimpleItem(_Item):
    
    def __init__(self, name, value, row, parent):
        _Item.__init__(self, name, row, parent)
        self.value = value

    def extend(self, value):
        self.value.extend(value)
        
    def copy(self):
        return SimpleItem(self.name, self.value[:], self._row, self._parent)
        

class ComplexItem(_Item):
    """Represents one item in Test Case or Keyword table"""
    
    def __init__(self, name, row, parent):
        _Item.__init__(self, name, row, parent)
        self.metadata = []
        self.keywords = []
        self._previous = None
        self._current_row = self._row - 1

    def add_subitem(self, data):
        self._current_row += 1
        if len(data) == 0: 
            return
        name = data[0]
        if name == '...':
            self._add_to_previous(data[1:])
        elif name == '' and len(data) > 1 and data[1] == '...':
            self._add_to_previous(data[2:])
        elif name.startswith('[') and name.endswith(']'):
            name = name[1:-1].strip()   # removes '[' and ']'
            item = SimpleItem(name, data[1:], self._current_row, self._parent)
            self.metadata.append(item)
            self._previous = self.metadata
        else:
            self.keywords.append(data)
            self._previous = self.keywords

    def _add_to_previous(self, data):
        if self._previous is None:
            raise DataError('Invalid multirow usage: No item started')
        self._previous[-1].extend(data)
