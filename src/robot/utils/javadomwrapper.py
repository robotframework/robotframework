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


from javax.xml.parsers import DocumentBuilderFactory
from java.io import FileInputStream, ByteArrayInputStream, StringReader
from org.xml.sax import InputSource, EntityResolver

from abstractdomwrapper import AbstractDomWrapper


class DomWrapper(AbstractDomWrapper):
    
    """A wrapper for Java's XML DOM for simplifying reading data from it.
    
    See documentation of AbstractDomWrapper for further usage information.
    """
    
    def __init__(self, path=None, string=None, node=None):
        """Initialize by giving 'path' to an xml file or xml as a 'string'.
        
        Alternative initialization by giving dom 'node' ment to be used only
        internallly.
        """
        AbstractDomWrapper.__init__(self, path)
        if node is None:
            node = self._get_root(path, string)
        self.name = node.tagName
        for item in self._create_list(node.attributes):
            self.attrs[item.name] = item.value
        for child in self._create_list(node.childNodes):
            if child.nodeType == child.ELEMENT_NODE:
                self.children.append(DomWrapper(path, node=child))
            elif child.nodeType == child.TEXT_NODE:
                self.text += child.data
            elif child.nodeType != child.COMMENT_NODE:
                raise TypeError("Unsupported node type: %s" % child.nodeType)

    def _get_dom(self, path, string):
        if path is not None:
            source = FileInputStream(path)
        else:
            source = ByteArrayInputStream(string)
        factory = DocumentBuilderFactory.newInstance()
        factory.setValidating(False)
        builder = factory.newDocumentBuilder()
        builder.setEntityResolver(_IgnoreDtd())
        return builder.parse(source, 'dummy base uri')
        
    def _create_list(self, items):
        return [ items.item(i) for i in range(items.length) ]

    
class _IgnoreDtd(EntityResolver):
    """EntityResolver that ignores all dtd references from doctypes.
    
    The idea to this hack is based on example at 
    http://books.evc-cit.info/oobook/apc.html
    """
    def resolveEntity(self, publicId, systemId):
        return InputSource(StringReader(''))
