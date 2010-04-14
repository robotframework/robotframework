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

from StringIO import StringIO
try:
    import xml.etree.cElementTree as ET
except ImportError:
    try:
        import cElementTree as ET
    except ImportError:
        try:
            import xml.etree.ElementTree as ET
        except ImportError:
            import elementtree.ElementTree as ET

from abstractdomwrapper import AbstractDomWrapper


class DomWrapper(AbstractDomWrapper):
    
    """A wrapper for Python's XML DOM for simplifying reading data from it.
    
    See documentation of AbstractDomWrapper for further usage information.
    """

    def __init__(self, path=None, string=None, node=None):
        """Initialize by giving 'path' to an xml file or xml as a 'string'.
        
        Alternative initialization by giving dom 'node' ment to be used only
        internally. 'path' may actually also be an already opened file object
        (or anything accepted by ElementTree.parse).
        """
        AbstractDomWrapper.__init__(self, path)
        # This should NOT be changed to 'if node:'. See chapter Truth Testing
        # from http://effbot.org/zone/element.htm#the-element-type 
        if node is None: 
            node = ET.parse(path or StringIO(string)).getroot()
        self.name = node.tag
        self.attrs = dict(node.items())
        self.text = node.text or ''
        for child in list(node):
            self.children.append(DomWrapper(path, node=child))
