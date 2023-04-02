import unittest

from robot.model import Body, BodyItem, If, For, Keyword, TestCase, TestSuite
from robot.result.model import Body as ResultBody
from robot.utils.asserts import assert_equal, assert_raises_with_msg


class TestBody(unittest.TestCase):

    def test_no_create(self):
        error = ("'robot.model.Body' object has no attribute 'create'. "
                 "Use item specific methods like 'create_keyword' instead.")
        assert_raises_with_msg(AttributeError, error,
                               getattr, Body(), 'create')
        assert_raises_with_msg(AttributeError, error.replace('.model.', '.result.'),
                               getattr, ResultBody(), 'create')

    def test_base_body_does_not_support_filtering_by_messages(self):
        error = "'robot.model.Body' object does not support filtering by 'messages'."
        assert_raises_with_msg(TypeError, error,
                               Body().filter, messages=True)
        assert_raises_with_msg(TypeError, error,
                               Body().filter, messages=False)

    def test_filter_when_messages_are_supported(self):
        body = ResultBody()
        k1 = body.create_keyword()
        m1 = body.create_message()
        i1 = body.create_if()
        f1 = body.create_for()
        i2 = body.create_if()
        k2 = body.create_keyword()
        m2 = body.create_message()
        m3 = body.create_message()
        assert_equal(body.filter(keywords=True), [k1, k2])
        assert_equal(body.filter(keywords=False), [m1, i1, f1, i2, m2, m3])
        assert_equal(body.filter(messages=True), [m1, m2, m3])
        assert_equal(body.filter(messages=False), [k1, i1, f1, i2, k2])
        assert_equal(body.filter(keywords=True, messages=True), [k1, m1, k2, m2, m3])
        assert_equal(body.filter(keywords=False, messages=False), [i1, f1, i2])
        assert_equal(body.filter(), [k1, m1, i1, f1, i2, k2, m2, m3])

    def test_cannot_filter_with_both_includes_and_excludes(self):
        assert_raises_with_msg(
            ValueError,
            'Items cannot be both included and excluded by type.',
            ResultBody().filter, keywords=True, messages=False
        )

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

    def test_id_when_item_not_in_parent(self):
        tc = TestCase(parent=TestSuite(parent=TestSuite()))
        assert_equal(tc.id, 's1-s1-t1')
        assert_equal(Keyword(parent=tc).id, 's1-s1-t1-k1')
        tc.body.create_keyword()
        tc.body.create_if().body.create_branch()
        assert_equal(Keyword(parent=tc).id, 's1-s1-t1-k3')

    def test_id_with_if(self):
        tc = TestCase()
        root = tc.body.create_if()
        assert_equal(root.id, None)
        branch = root.body.create_branch()
        assert_equal(branch.id, 't1-k1')
        assert_equal(branch.body.create_keyword().id, 't1-k1-k1')
        assert_equal(branch.body.create_keyword().id, 't1-k1-k2')
        branch = root.body.create_branch()
        assert_equal(branch.id, 't1-k2')
        assert_equal(branch.body.create_keyword().id, 't1-k2-k1')
        assert_equal(branch.body.create_keyword().id, 't1-k2-k2')
        assert_equal(tc.body.create_keyword().id, 't1-k3')

    def test_id_with_try(self):
        tc = TestCase()
        root = tc.body.create_try()
        assert_equal(root.id, None)
        branch = root.body.create_branch()
        assert_equal(branch.id, 't1-k1')
        assert_equal(branch.body.create_keyword().id, 't1-k1-k1')
        assert_equal(branch.body.create_keyword().id, 't1-k1-k2')
        branch = root.body.create_branch()
        assert_equal(branch.id, 't1-k2')
        assert_equal(branch.body.create_keyword().id, 't1-k2-k1')
        assert_equal(branch.body.create_keyword().id, 't1-k2-k2')
        assert_equal(tc.body.create_keyword().id, 't1-k3')

    def test_id_with_if_and_try(self):
        tc = TestCase()
        # IF
        root = tc.body.create_if()
        assert_equal(root.id, None)
        branch = root.body.create_branch()
        assert_equal(branch.id, 't1-k1')
        assert_equal(branch.body.create_keyword().id, 't1-k1-k1')
        assert_equal(branch.body.create_keyword().id, 't1-k1-k2')
        branch = root.body.create_branch()
        assert_equal(branch.id, 't1-k2')
        assert_equal(branch.body.create_keyword().id, 't1-k2-k1')
        assert_equal(branch.body.create_keyword().id, 't1-k2-k2')
        assert_equal(tc.body.create_keyword().id, 't1-k3')
        # TRY
        root = tc.body.create_try()
        assert_equal(root.id, None)
        branch = root.body.create_branch()
        assert_equal(branch.id, 't1-k4')
        assert_equal(branch.body.create_keyword().id, 't1-k4-k1')
        assert_equal(branch.body.create_keyword().id, 't1-k4-k2')
        branch = root.body.create_branch()
        assert_equal(branch.id, 't1-k5')
        assert_equal(branch.body.create_keyword().id, 't1-k5-k1')
        assert_equal(branch.body.create_keyword().id, 't1-k5-k2')
        assert_equal(tc.body.create_keyword().id, 't1-k6')
        # IF again
        root = tc.body.create_if()
        assert_equal(root.id, None)
        branch = root.body.create_branch()
        assert_equal(branch.id, 't1-k7')
        assert_equal(branch.body.create_keyword().id, 't1-k7-k1')
        assert_equal(branch.body.create_keyword().id, 't1-k7-k2')
        branch = root.body.create_branch()
        assert_equal(branch.id, 't1-k8')
        assert_equal(branch.body.create_keyword().id, 't1-k8-k1')
        assert_equal(branch.body.create_keyword().id, 't1-k8-k2')
        assert_equal(tc.body.create_keyword().id, 't1-k9')


if __name__ == '__main__':
    unittest.main()
