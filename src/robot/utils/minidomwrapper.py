#  Copyright 2008 Nokia Siemens Networks Oyj
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


from xml.dom import minidom
from StringIO import StringIO

from abstractdomwrapper import AbstractDomWrapper


class DomWrapper(AbstractDomWrapper):
    
    """A wrapper for Python's XML DOM for simplifying reading data from it.
    
    See documentation of AbstractDomWrapper for further usage information.
    """

    def __init__(self, path=None, string=None, node=None):
        """Initialize by giving 'path' to an xml file or xml as a 'string'.
        
        Alternative initialization by giving dom 'node' ment to be used only
        internally. 'path' may actually also be an already opened file object
        (or anything accepted by minidom.parse).
        """
        AbstractDomWrapper.__init__(self, path)
        if node is None:
            node = self._get_root(path, string)
        self.name = node.tagName
        self.attrs = dict(node.attributes.items())
        for child in node.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                self.children.append(DomWrapper(path, node=child))
            elif child.nodeType == child.TEXT_NODE:
                self.text += child.data
            elif child.nodeType != child.COMMENT_NODE:
                raise TypeError("Unsupported node type: %s" % child.nodeType)

    def _get_dom(self, path, string):
        if path is not None:
            source = path
        else:
            source = StringIO(string)
        return minidom.parse(source)
