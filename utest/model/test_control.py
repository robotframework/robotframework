import unittest
import warnings

from robot.model import For, If, Tags
from robot.utils import PY2, unicode
from robot.utils.asserts import assert_equal, assert_false, assert_true


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
            assert_equal(unicode(for_), exp_str)
            assert_equal(repr(for_), 'robot.model.' + exp_repr)
            if PY2:
                assert_equal(str(for_), unicode(for_).encode('UTF-8'))


class TestIf(unittest.TestCase):

    def test_type(self):
        assert_equal(If().type, If.IF_TYPE)
        assert_equal(If(type=If.ELSE_TYPE).type, If.ELSE_TYPE)
        assert_equal(If(type=If.ELSE_IF_TYPE).type, If.ELSE_IF_TYPE)
        assert_equal(If(type=None).type, None)

    def test_config_does_not_set_type_if_its_set(self):
        assert_equal(If().config().type, If.IF_TYPE)
        assert_equal(If(type=If.ELSE_TYPE).config().type, If.ELSE_TYPE)
        assert_equal(If(type=If.ELSE_IF_TYPE).config().type, If.ELSE_IF_TYPE)
        assert_equal(If(type=None).config(type=If.IF_TYPE).type, If.IF_TYPE)
        assert_equal(If(type=None).config(type=If.ELSE_TYPE).type, If.ELSE_TYPE)
        assert_equal(If(type=None).config(type=If.ELSE_IF_TYPE).type, If.ELSE_IF_TYPE)

    def test_config_sets_type_if_its_not_set(self):
        assert_equal(If(type=None).config().type, If.ELSE_TYPE)
        assert_equal(If(type=None).config(condition='$x > 0').type, If.ELSE_IF_TYPE)

    def test_orelse_type(self):
        assert_equal(If().orelse.type, None)
        assert_equal(If().orelse.config().type, If.ELSE_TYPE)
        assert_equal(If().orelse.config(condition='$x').type, If.ELSE_IF_TYPE)
        assert_equal(If().orelse.config(condition='$x').orelse.type, None)
        assert_equal(If().orelse.config(condition='$x').orelse.config().type, If.ELSE_TYPE)

    def test_type_with_nested_if(self):
        assert_equal(If().body.create_if().type, If.IF_TYPE)
        assert_equal(If().body.create_if().orelse.type, None)
        assert_equal(If().body.create_if().orelse.config().type, If.ELSE_TYPE)

    def test_orelse(self):
        self._validate_orelse(If().orelse)
        self._validate_orelse(If().orelse.config().orelse)
        self._validate_orelse(If().orelse.config().orelse.config().orelse)

    def _validate_orelse(self, orelse):
        assert_false(orelse)
        assert_equal(orelse.type, None)
        assert_equal(orelse.orelse, None)
        orelse.config()
        assert_true(orelse)
        assert_equal(orelse.type, If.ELSE_TYPE)
        assert_false(orelse.orelse)
        assert_equal(orelse.orelse.type, None)

    def test_string_reprs(self):
        for if_, exp_str, exp_repr in [
            (If(),
             'IF    None',
             "If(condition=None, type='if')"),
            (If('$x > 1'),
             'IF    $x > 1',
             "If(condition='$x > 1', type='if')"),
            (If().orelse.config(condition='$x > 2'),
             'ELSE IF    $x > 2',
             "If(condition='$x > 2', type='elseif')"),
            (If().orelse.config(),
             'ELSE',
             "If(condition=None, type='else')"),
            (If().orelse,
             'None',
             "If(condition=None, type=None)"),
            (If(u'$x == "\xe4iti"'),
             u'IF    $x == "\xe4iti"',
             u"If(condition=%r, type='if')" % u'$x == "\xe4iti"'),
        ]:
            assert_equal(unicode(if_), exp_str)
            assert_equal(repr(if_), 'robot.model.' + exp_repr)
            if PY2:
                assert_equal(str(if_), unicode(if_).encode('UTF-8'))


if __name__ == '__main__':
    unittest.main()
