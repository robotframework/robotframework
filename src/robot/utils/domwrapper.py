#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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


class DomWrapper(object):
    
    """A wrapper for Python's XML DOM for simplifying reading data from it.
    
    See documentation of AbstractDomWrapper for further usage information.
    """

    def __init__(self, path=None, string=None, node=None):
        """Initialize by giving 'path' to an xml file or xml as a 'string'.
        
        Alternative initialization by giving dom 'node' ment to be used only
        internally. 'path' may actually also be an already opened file object
        (or anything accepted by ElementTree.parse).
        """
        node = self._get_node(path, string, node)
        self.source = path
        self.name = node.tag
        self.attrs = dict(node.items())
        self.text = node.text or ''
        self.children = [ DomWrapper(path, node=child) for child in list(node) ]

    def _get_node(self, path, string, node):
        # This should NOT be changed to 'if not node:'. See chapter Truth Testing
        # from http://effbot.org/zone/element.htm#the-element-type 
        if node is not None:
            return node
        # Cannot give path to ET.parse because it doesn't close files it opens
        # http://bugs.jython.org/issue1598
        if path:
            source = open(path, 'rb')
        else:
            source = StringIO(string)
        try:
            return ET.parse(source).getroot()
        finally:
            source.close()

    def get_nodes(self, path):
        """Returns a list of descendants matching given 'path'.

        Path must be a string in format 'child_name/grandchild_name/etc'. No
        slash is allowed at the beginning or end of the path string. Returns an
        empty list if no matching descendants found and raises AttributeError
        if path is invalid.
        """
        if not isinstance(path, basestring) \
           or path == '' or path[0] == '/' or path[-1] == '/':
            raise AttributeError("Invalid path '%s'" % path)
        matches = []
        for child in self.children:
            matches += child._get_matching_elements(path.split('/'))
        return matches

    def _get_matching_elements(self, tokens):
        if self.name != tokens[0]:
            return []
        elif len(tokens) == 1:
            return [self]
        else:
            matches = []
            for child in self.children:
                matches += child._get_matching_elements(tokens[1:])
            return matches

    def get_node(self, path):
        """Similar as get_nodes but checks that exactly one node is found.

        Node is returned as is (i.e. not in a list) and AttributeError risen if
        no match or more than one match found.
        """
        nodes = self.get_nodes(path)
        if len(nodes) == 0:
            raise AttributeError("No nodes matching path '%s' found" % path)
        if len(nodes) > 1:
            raise AttributeError("Multiple nodes matching path '%s' found" % path)
        return nodes[0]

    def get_attr(self, name, default=None):
        """Helper for getting node's attributes.

        Otherwise equivalent to 'node.attrs.get(name, default)' but raises
        an AttributeError if no value found and no default given.
        """
        ret = self.attrs.get(name, default)
        if ret is None:
            raise AttributeError("No attribute '%s' found" % name)
        return ret

    def __getattr__(self, name):
        """Syntactic sugar for get_nodes (e.g. dom.elem[0].subelem).

        Differs from get_nodes so that if not matching nodes are found an
        AttributeError is risen instead of returning an empty list.
        """
        nodes = self.get_nodes(name)
        if not nodes:
            raise AttributeError("No nodes matching path '%s' found" % name)
        return nodes

    def __getitem__(self, name):
        """Syntactic sugar for get_node (e.g. dom['elem/subelem'])"""
        try:
            return self.get_node(name)
        except AttributeError:
            raise IndexError("No node '%s' found" % name)

    def __repr__(self):
        """Return node name. Mainly for debugging purposes."""
        return self.name
