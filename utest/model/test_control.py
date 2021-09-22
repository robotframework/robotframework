import unittest

from robot.model import For, If, IfBranch, TestCase
from robot.utils.asserts import assert_equal


IF = If.IF
ELSE_IF = If.ELSE_IF
ELSE = If.ELSE


class TestFor(unittest.TestCase):

    def test_string_reprs(self):
        for for_, exp_str, exp_repr in [
            (For(),
             'FOR        IN    ',
             "For(variables=(), flavor='IN', values=())"),
            (For(('${x}',), 'IN RANGE', ('10',)),
             'FOR    ${x}    IN RANGE    10',
             "For(variables=('${x}',), flavor='IN RANGE', values=('10',))"),
            (For(('${x}', '${y}'), 'IN ENUMERATE', ('a', 'b')),
             'FOR    ${x}    ${y}    IN ENUMERATE    a    b',
             "For(variables=('${x}', '${y}'), flavor='IN ENUMERATE', values=('a', 'b'))"),
            (For([u'${\xfc}'], 'IN', [u'f\xf6\xf6']),
             u'FOR    ${\xfc}    IN    f\xf6\xf6',
             u"For(variables=[%r], flavor='IN', values=[%r])" % (u'${\xfc}', u'f\xf6\xf6'))
        ]:
            assert_equal(str(for_), exp_str)
            assert_equal(repr(for_), 'robot.model.' + exp_repr)


class TestIf(unittest.TestCase):

    def test_type(self):
        assert_equal(IfBranch().type, IF)
        assert_equal(IfBranch(type=ELSE).type, ELSE)
        assert_equal(IfBranch(type=ELSE_IF).type, ELSE_IF)

    def test_type_with_nested_if(self):
        branch = IfBranch()
        branch.body.create_if()
        assert_equal(branch.body[0].body.create_branch().type, IF)
        assert_equal(branch.body[0].body.create_branch(ELSE_IF).type, ELSE_IF)
        assert_equal(branch.body[0].body.create_branch(ELSE).type, ELSE)

    def test_root_id(self):
        assert_equal(If().id, None)
        assert_equal(TestCase().body.create_if().id, None)

    def test_branch_id_without_parent(self):
        assert_equal(IfBranch().id, 'k1')

    def test_branch_id_with_only_root(self):
        root = If()
        assert_equal(root.body.create_branch().id, 'k1')
        assert_equal(root.body.create_branch().id, 'k2')

    def test_branch_id_with_real_parent(self):
        root = TestCase().body.create_if()
        assert_equal(root.body.create_branch().id, 't1-k1')
        assert_equal(root.body.create_branch().id, 't1-k2')

    def test_string_reprs(self):
        for if_, exp_str, exp_repr in [
            (IfBranch(),
             'IF    None',
             "IfBranch(type='IF', condition=None)"),
            (IfBranch(condition='$x > 1'),
             'IF    $x > 1',
             "IfBranch(type='IF', condition='$x > 1')"),
            (IfBranch(ELSE_IF, condition='$x > 2'),
             'ELSE IF    $x > 2',
             "IfBranch(type='ELSE IF', condition='$x > 2')"),
            (IfBranch(ELSE),
             'ELSE',
             "IfBranch(type='ELSE', condition=None)"),
            (IfBranch(condition=u'$x == "\xe4iti"'),
             u'IF    $x == "\xe4iti"',
             u"IfBranch(type='IF', condition=%r)" % u'$x == "\xe4iti"'),
        ]:
            assert_equal(str(if_), exp_str)
            assert_equal(repr(if_), 'robot.model.' + exp_repr)


if __name__ == '__main__':
    unittest.main()
