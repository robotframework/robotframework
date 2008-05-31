import unittest, sys, StringIO

from robot.utils.asserts import *
from robot.serializing.templating import Template, Namespace


class TemplateWithOverridenInit(Template):
    def __init__(self):
        pass
    
T = TemplateWithOverridenInit
N = Namespace


class TestTemplate(unittest.TestCase):
    

    def test_replace_nothing(self):
        t = T()
        t._namespace = N()
        assert_equals(t._handle_variables('hi world') , 'hi world')

    def test_replace_string(self):
        t = T()
        handler = t._handle_variables
        t._namespace = N(name='world')
        assert_equals(handler('hi ${name}'), 'hi world')
        t._namespace = N(name='moon')
        assert_equals(handler('hi ${name}'), 'hi moon')
        t._namespace = N(f='h',o='a')
        assert_equals(handler('${f}${o}${o}'), 'haa')

    def test_if(self):
        template = '1\n<!-- IF ${x} == 0 -->\n${num}\n<!-- END IF -->\n3\n'
        temp = Template(template=template)
        assert_equals(temp.generate(N(num='2',x=0)), '1\n2\n3')
        assert_equals(temp.generate(N(num='2',x=1)), '1\n3')

    def test_if_else(self):
        template = '1\n<!-- IF ${x} == 0 -->\na = ${a}\n<!-- ELSE -->\n'
        template += 'b = ${b}\n<!-- END IF -->\n3'
        temp = Template(template=template)
        assert_equals(temp.generate(N(a='a',b='b',x=0)), '1\na = a\n3')
        assert_equals(temp.generate(N(a='a',b='b',x=1)), '1\nb = b\n3')

    def test_very_long_if_else(self):
        at = 25000
        bt = 10000
        template = '1\n<!-- IF ${x} == 0 -->\n'
        template += 'a'*at
        template += '\n<!-- ELSE -->\n'
        template += 'b'*bt
        template += '\n<!-- END IF -->\n3'
        temp = Template(template=template)
        assert_equals(temp.generate(N(x=0)), '1\n%s\n3' % ('a'*at))
        assert_equals(temp.generate(N(x=1)), '1\n%s\n3' % ('b'*bt))

    def test_two_ifs(self):
        template = '1\n<!-- IF ${x} == 0 -->\nx=0\n<!-- ELSE -->\nx=1\n<!-- END IF -->\n2\n'
        template += '3\n<!-- IF ${y} == 0 -->\ny=0\n<!-- ELSE -->\ny=1\n<!-- END IF -->\n4\n'
        temp = Template(template=template)
        assert_equals(temp.generate(N(x=0, y=0)), '1\nx=0\n2\n3\ny=0\n4')

    def test_for(self):
        template = '0\n<!-- FOR ${num} in ${numbers} -->\n'
        template += '${num}\n'
        template += '<!-- END FOR -->\n10\n'
        temp = Template(template=template)
        assert_equals(temp.generate(N(x=0, numbers=[])), '0\n10')
        assert_equals(temp.generate(N(x=0, numbers='1 2 3 4 5 6 7 8 9'.split())), 
                      '0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n10')

    def test_for_with_if_inside(self):
        template = '1\n<!-- FOR ${test} in ${tests} -->\n'
        template += '<!-- IF ${x} == 0 -->\n'
        template += 'name:${test}\n'
        template += '<!-- END IF -->\n'
        template += '<!-- END FOR -->\n2\n'
        temp = Template(template=template)
        assert_equals(temp.generate(N(x=0, tests=[])), '1\n2')
        assert_equals(temp.generate(N(x=0, tests=['test1', 'test2'])), 
                      '1\nname:test1\nname:test2\n2')

    def test_functions(self):
        template = '1\n'
        template += '<!-- FUNCTION func1 ${arg1} ${arg2} -->\n'
        template += ' Hello ${arg1}!\nHi ${arg2}\n'
        template += '<!-- END FUNCTION -->\n'
        template += '2\n'
        template += '<!-- FUNCTION func2 -->\nHi you!\n<!-- END FUNCTION -->\n'
        template += '3\n'
        temp = Template(template=template)
        temp.generate(N())
        for name, args, body in [
            ( 'func1', ['${arg1}', '${arg2}'], ' Hello ${arg1}!\nHi ${arg2}'),
            ( 'func2', [], 'Hi you!')
            ]:
            assert_true(temp._functions.has_key(name))
            act_args, act_body = temp._functions[name]
            assert_equals(act_args, args)
            assert_equals(act_body, body)

    def test_call(self):
        temp = Template(template='''
<!-- FUNCTION func1 ${arg1} ${arg2} -->
Hello ${arg1}!
Hi ${arg2}
<!-- END FUNCTION -->

<!-- FUNCTION func2 -->
Hi you!
<!-- END FUNCTION -->

<!-- CALL func1 world me -->
<!-- CALL func2 -->
''')
        assert_equals(temp.generate(N()), '''


Hello world!
Hi me
Hi you!''')

    def test_output(self):
        temp = Template(template='''
<!-- FUNCTION func1 ${arg1} ${arg2} -->
  Hello ${arg1}!
  Hi ${arg2}!
<!-- END FUNCTION -->
<!-- FUNCTION func2 -->
Hi you!
<!-- END FUNCTION -->

<!-- CALL func1 world me -->

<!-- CALL func2 -->

${hello}
''')
        output = StringIO.StringIO()
        ret = temp.generate(N(hello='Hi tellus!'), output)
        assert_none(ret)
        output.flush()
        assert_equals(output.getvalue(), '''

  Hello world!
  Hi me!

Hi you!

Hi tellus!
''')


if __name__ == '__main__':
    unittest.main()
