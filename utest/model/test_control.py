import unittest
import warnings

from robot.model import For, If, Tags
from robot.utils import PY2, unicode
from robot.utils.asserts import assert_equal, assert_true


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

    def test_deprecated_keyword_specific_properties(self):
        class NotDeprecated(For):
            deprecate_keyword_attributes = False

        deprecated = For(['${x}', '${y}'], 'IN', ['a', 'b', 'c', 'd'])
        not_deprecated = NotDeprecated(['${x}', '${y}'], 'IN', ['a', 'b', 'c', 'd'])

        for name, expected in [('name', '${x} | ${y} IN [ a | b | c | d ]'),
                               ('doc', ''),
                               ('args', ()),
                               ('assign', ()),
                               ('tags', Tags()),
                               ('timeout', None)]:
            with warnings.catch_warnings(record=True) as w:
                assert_equal(getattr(not_deprecated, name), expected)
                assert_equal(len(w), 0)
                assert_equal(getattr(deprecated, name), expected)
                assert_equal(str(w[0].message), "'For.%s' is deprecated." % name)
                assert_equal(w[0].category, UserWarning)


class TestIf(unittest.TestCase):

    def test_string_reprs(self):
        for if_, exp_str, exp_repr in [
            (If(),
             'IF    None',
             'If(condition=None)'),
            (If('$x > 1'),
             'IF    $x > 1',
             "If(condition='$x > 1')"),
            (If().orelse.config(condition='$x > 2'),
             'ELSE IF    $x > 2',
             "If(condition='$x > 2')"),
            (If().orelse.config(condition=None),
             'ELSE',
             'If(condition=None)'),
            (If().orelse,
             'None',
             'If(condition=INACTIVE)'),
            (If(u'$x == "\xe4iti"'),
             u'IF    $x == "\xe4iti"',
             u'If(condition=%r)' % u'$x == "\xe4iti"'),
        ]:
            assert_equal(unicode(if_), exp_str)
            assert_equal(repr(if_), 'robot.model.' + exp_repr)
            if PY2:
                assert_equal(str(if_), unicode(if_).encode('UTF-8'))

    def test_deprecated_keyword_specific_properties(self):
        class NotDeprecated(If):
            deprecate_keyword_attributes = False

        deprecated = If('$x > 0')
        not_deprecated = NotDeprecated('$x > 0')

        for name, expected in [('name', '$x > 0'),
                               ('doc', ''),
                               ('args', ()),
                               ('assign', ()),
                               ('tags', Tags()),
                               ('timeout', None)]:
            with warnings.catch_warnings(record=True) as w:
                assert_equal(getattr(not_deprecated, name), expected)
                assert_equal(len(w), 0)
                assert_equal(getattr(deprecated, name), expected)
                assert_equal(str(w[0].message), "'If.%s' is deprecated." % name)
                assert_equal(w[0].category, UserWarning)


if __name__ == '__main__':
    unittest.main()
