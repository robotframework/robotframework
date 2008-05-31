import sys, unittest, StringIO

if __name__ == "__main__":
    sys.path.insert(0, "../../../src")

from robot.utils.asserts import *

from robot.utils import DomWrapper


XML_STR = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root PUBLIC "-//BLAA/BLAA//EN" "nonexisting.dtd">
<!-- Comment before root - all comments (and doctypes) should be ignored -->
<root>
  <!-- Comment inside root -->
  <elem a1="v1" a2="v2">
    <txt>hello</txt>
    <!-- Comment again -->
  </elem>
  <elem/>
  <!-- 
       Multiline
       comment
  <elem><txt>still in comment</txt></elem>  
  -->
  <elem a="v">
    <elem>
      <txt>hi</txt>
    </elem>
    <elem>
      <txt/>
    </elem>
  </elem>
</root>
<!-- Comment after root -->
'''
    
# Tests only read from dom so we can create it only once
DOM = DomWrapper(string=XML_STR)


class TestDomWrapper(unittest.TestCase):
    
    def test_root(self):
        assert_equals(DOM.name, 'root')
        assert_equals(DOM.attrs, {})

    def test_elem(self): 
        e1 = DOM.elem[0]   # using __getattr__ sugar
        e2 = DOM.elem[1]
        e3 = DOM.elem[2]
        e31 = e3.elem[0]
        e32 = e3.elem[1]
        for elem, exp_attrs in [ (e1,{'a1':'v1','a2':'v2'}), (e2,{}),
                                 (e3,{'a':'v'}), (e31,{}), (e32,{}) ]:
            assert_equals(elem.name, 'elem')
            assert_equals(elem.attrs, exp_attrs)
            
    def test_text(self):
        t1 = DOM.elem[0].txt[0]
        t2 = DOM.elem[2].elem[0].txt[0]
        t3 = DOM.elem[2].elem[1].txt[0]
        for elem, exp_text in [ (t1,'hello'), (t2,'hi'), (t3,'') ]:
            assert_equals(elem.name, 'txt')
            assert_equals(elem.text, exp_text)
            assert_equals(elem.attrs, {})
            assert_equals(elem.children, [])
            
    def test_get_nodes(self):
        nodes = DOM.get_nodes('elem/txt')
        assert_equals(len(nodes), 1)
        assert_equals(nodes[0].text, 'hello')
        nodes = DOM.get_nodes('elem/elem/txt')
        assert_equals(len(nodes), 2)
        assert_equals(nodes[0].text, 'hi')
        assert_equals(nodes[1].text, '')        

    def test_sugar(self):
        node = DOM.get_nodes('elem')[0].get_node('txt')
        assert_equals(DOM.elem[0].txt[0], node)
        assert_equals(DOM['elem/txt'], node)
        assert_raises(AttributeError, DOM.__getattr__, 'nonexisting')
        assert_raises(IndexError, DOM.__getitem__, 'nonexisting')
        assert_raises(IndexError, DOM.__getitem__, 2)
        
                                
if __name__ == "__main__":
    unittest.main()
