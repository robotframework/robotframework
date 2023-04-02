import unittest

from robot.model import For, If, IfBranch, TestCase, Try, TryBranch, While
from robot.utils.asserts import assert_equal


IF = If.IF
ELSE_IF = If.ELSE_IF
ELSE = If.ELSE
TRY = Try.TRY
EXCEPT = Try.EXCEPT
FINALLY = Try.FINALLY


class TestFor(unittest.TestCase):

    def test_string_reprs(self):
        for for_, exp_str, exp_repr in [
            (For(),
             'FOR    IN',
             "For(variables=(), flavor='IN', values=())"),
            (For(('${x}',), 'IN RANGE', ('10',)),
             'FOR    ${x}    IN RANGE    10',
             "For(variables=('${x}',), flavor='IN RANGE', values=('10',))"),
            (For(('${x}', '${y}'), 'IN ENUMERATE', ('a', 'b')),
             'FOR    ${x}    ${y}    IN ENUMERATE    a    b',
             "For(variables=('${x}', '${y}'), flavor='IN ENUMERATE', values=('a', 'b'))"),
            (For(['${x}'], 'IN ENUMERATE', ['@{stuff}'], start='1'),
             'FOR    ${x}    IN ENUMERATE    @{stuff}    start=1',
             "For(variables=['${x}'], flavor='IN ENUMERATE', values=['@{stuff}'], start='1')"),
            (For(('${x}', '${y}'), 'IN ZIP', ('${xs}', '${ys}'), mode='LONGEST', fill='-'),
             'FOR    ${x}    ${y}    IN ZIP    ${xs}    ${ys}    mode=LONGEST    fill=-',
             "For(variables=('${x}', '${y}'), flavor='IN ZIP', values=('${xs}', '${ys}'), mode='LONGEST', fill='-')"),
            (For(['${ü}'], 'IN', ['föö']),
             'FOR    ${ü}    IN    föö',
             "For(variables=['${ü}'], flavor='IN', values=['föö'])")
        ]:
            assert_equal(str(for_), exp_str)
            assert_equal(repr(for_), 'robot.model.' + exp_repr)


class TestWhile(unittest.TestCase):

    def test_string_reprs(self):
        for while_, exp_str, exp_repr in [
            (While(),
             'WHILE',
             "While(condition=None)"),
            (While('$x', limit='100'),
             'WHILE    $x    limit=100',
             "While(condition='$x', limit='100')")
        ]:
            assert_equal(str(while_), exp_str)
            assert_equal(repr(while_), 'robot.model.' + exp_repr)


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

    def test_branch_id_with_only_root_when_branch_not_in_root(self):
        assert_equal(IfBranch(parent=If()).id, 'k1')

    def test_branch_id_with_real_parent(self):
        root = TestCase().body.create_if()
        assert_equal(root.body.create_branch().id, 't1-k1')
        assert_equal(root.body.create_branch().id, 't1-k2')

    def test_branch_id_when_parent_has_setup(self):
        tc = TestCase()
        assert_equal(tc.setup.config(name='X').id, 't1-k1')
        assert_equal(tc.body.create_keyword().id, 't1-k2')
        assert_equal(tc.body.create_if().body.create_branch().id, 't1-k3')
        assert_equal(tc.body.create_keyword().id, 't1-k4')
        assert_equal(tc.body.create_if().body.create_branch().id, 't1-k5')

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


class TestTry(unittest.TestCase):

    def test_type(self):
        assert_equal(TryBranch().type, TRY)
        assert_equal(TryBranch(type=EXCEPT).type, EXCEPT)
        assert_equal(TryBranch(type=ELSE).type, ELSE)
        assert_equal(TryBranch(type=FINALLY).type, FINALLY)

    def test_type_with_nested_Try(self):
        branch = TryBranch()
        branch.body.create_try()
        assert_equal(branch.body[0].body.create_branch().type, TRY)
        assert_equal(branch.body[0].body.create_branch(type=EXCEPT).type, EXCEPT)
        assert_equal(branch.body[0].body.create_branch(type=ELSE).type, ELSE)
        assert_equal(branch.body[0].body.create_branch(type=FINALLY).type, FINALLY)

    def test_root_id(self):
        assert_equal(Try().id, None)
        assert_equal(TestCase().body.create_try().id, None)

    def test_branch_id_without_parent(self):
        assert_equal(TryBranch().id, 'k1')

    def test_branch_id_with_only_root(self):
        root = Try()
        assert_equal(root.body.create_branch().id, 'k1')
        assert_equal(root.body.create_branch().id, 'k2')

    def test_branch_id_with_only_root_when_branch_not_in_root(self):
        assert_equal(TryBranch(parent=Try()).id, 'k1')

    def test_branch_id_with_real_parent(self):
        root = TestCase().body.create_try()
        assert_equal(root.body.create_branch().id, 't1-k1')
        assert_equal(root.body.create_branch().id, 't1-k2')

    def test_branch_id_when_parent_has_setup(self):
        tc = TestCase()
        assert_equal(tc.setup.config(name='X').id, 't1-k1')
        assert_equal(tc.body.create_keyword().id, 't1-k2')
        assert_equal(tc.body.create_try().body.create_branch().id, 't1-k3')
        assert_equal(tc.body.create_keyword().id, 't1-k4')
        assert_equal(tc.body.create_try().body.create_branch().id, 't1-k5')

    def test_string_reprs(self):
        for try_, exp_str, exp_repr in [
            (TryBranch(),
             'TRY',
             "TryBranch(type='TRY')"),
            (TryBranch(EXCEPT),
             'EXCEPT',
             "TryBranch(type='EXCEPT')"),
            (TryBranch(EXCEPT, ('Message',)),
             'EXCEPT    Message',
             "TryBranch(type='EXCEPT', patterns=('Message',))"),
            (TryBranch(EXCEPT, ('M', 'S', 'G', 'S')),
             'EXCEPT    M    S    G    S',
             "TryBranch(type='EXCEPT', patterns=('M', 'S', 'G', 'S'))"),
            (TryBranch(EXCEPT, (), None, '${x}'),
             'EXCEPT    AS    ${x}',
             "TryBranch(type='EXCEPT', variable='${x}')"),
            (TryBranch(EXCEPT, ('Message',), 'glob', '${x}'),
             'EXCEPT    Message    type=glob    AS    ${x}',
             "TryBranch(type='EXCEPT', patterns=('Message',), pattern_type='glob', variable='${x}')"),
            (TryBranch(ELSE),
             'ELSE',
             "TryBranch(type='ELSE')"),
            (TryBranch(FINALLY),
             'FINALLY',
             "TryBranch(type='FINALLY')"),
        ]:
            assert_equal(str(try_), exp_str)
            assert_equal(repr(try_), 'robot.model.' + exp_repr)


if __name__ == '__main__':
    unittest.main()
