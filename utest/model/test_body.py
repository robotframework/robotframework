import unittest

from robot.model import Body, BodyItem, If, For, Keyword, TestCase
from robot.utils.asserts import assert_equal, assert_raises


class TestBody(unittest.TestCase):

    def test_filter(self):
        k1, k2, k3 = Keyword(), Keyword(), Keyword()
        f1, i1, i2 = For(), If(), If()
        items = [k1, f1, i1, i2, k2, k3]
        body = Body(items=items)
        assert_equal(body.filter(keywords=True), [k1, k2, k3])
        assert_equal(body.filter(keywords=False), [f1, i1, i2])
        assert_equal(body.filter(ifs=True, fors=True), [f1, i1, i2])
        assert_equal(body.filter(ifs=True, fors=True), [f1, i1, i2])
        assert_equal(body.filter(), [k1, f1, i1, i2, k2, k3])

    def test_filter_with_includes_and_excludes_fails(self):
        assert_raises(ValueError, Body().filter, keywords=True, ifs=False)

    def test_filter_with_predicate(self):
        x = Keyword(name='x')
        predicate = lambda item: item.name == 'x'
        body = Body(items=[Keyword(), x, Keyword()])
        assert_equal(body.filter(predicate=predicate), [x])
        body = Body(items=[Keyword(), If(), x, For(), Keyword()])
        assert_equal(body.filter(keywords=True, predicate=predicate), [x])


class TestBodyItem(unittest.TestCase):

    def test_id_without_parent(self):
        item = BodyItem()
        item.parent = None
        assert_equal(item.id, 'k1')

    def test_id_with_parent(self):
        tc = TestCase()
        tc.body = [BodyItem(), BodyItem(), BodyItem()]
        assert_equal([item.id for item in tc.body], ['t1-k1', 't1-k2', 't1-k3'])

    def test_id_with_parent_having_setup_and_teardown(self):
        tc = TestCase()
        assert_equal(tc.setup.config(name='S').id, 't1-k1')
        assert_equal(tc.teardown.config(name='T').id, 't1-k2')
        tc.body = [BodyItem(), BodyItem(), BodyItem()]
        assert_equal([item.id for item in tc.body], ['t1-k2', 't1-k3', 't1-k4'])
        assert_equal(tc.setup.id, 't1-k1')
        assert_equal(tc.teardown.id, 't1-k5')


if __name__ == '__main__':
    unittest.main()
