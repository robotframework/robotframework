import unittest

from robot.model import (
    BaseBody, Body, BodyItem, For, If, Keyword, Message, TestCase, TestSuite, Try
)
from robot.result.model import Body as ResultBody, TestCase as ResultTestCase
from robot.utils.asserts import assert_equal, assert_raises, assert_raises_with_msg


def subclasses(base):
    for cls in base.__subclasses__():
        if cls.__module__.split(".")[0] != "robot":
            continue
        yield cls
        yield from subclasses(cls)


class TestBody(unittest.TestCase):

    def test_no_create(self):
        error = (
            "'robot.model.Body' object has no attribute 'create'. "
            "Use item specific methods like 'create_keyword' instead."
        )
        assert_raises_with_msg(
            AttributeError,
            error,
            getattr,
            Body(),
            "create",
        )
        assert_raises_with_msg(
            AttributeError,
            error.replace(".model.", ".result."),
            getattr,
            ResultBody(),
            "create",
        )

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

    def test_filter_when_messages_are_not_supported(self):
        body = Body()
        k1 = body.create_keyword()
        i1 = body.create_if()
        f1 = body.create_for()
        i2 = body.create_if()
        k2 = body.create_keyword()
        assert_equal(body.filter(keywords=True), [k1, k2])
        assert_equal(body.filter(keywords=False), [i1, f1, i2])
        assert_equal(body.filter(messages=True), [])
        assert_equal(body.filter(messages=False), [k1, i1, f1, i2, k2])
        assert_equal(body.filter(keywords=True, messages=True), [k1, k2])
        assert_equal(body.filter(keywords=False, messages=False), [i1, f1, i2])
        assert_equal(body.filter(), [k1, i1, f1, i2, k2])

    def test_cannot_filter_with_both_includes_and_excludes(self):
        assert_raises_with_msg(
            ValueError,
            "Items cannot be both included and excluded by type.",
            ResultBody().filter,
            keywords=True,
            messages=False,
        )

    def test_filter_with_predicate(self):
        x = Keyword(name="x")
        predicate = lambda item: item.name == "x"
        body = Body(items=[Keyword(), x, Keyword()])
        assert_equal(body.filter(predicate=predicate), [x])
        body = Body(items=[Keyword(), If(), x, For(), Keyword()])
        assert_equal(body.filter(keywords=True, predicate=predicate), [x])

    def test_all_body_classes_have_slots(self):
        for cls in subclasses(BaseBody):
            assert_raises(AttributeError, setattr, cls(None), "attr", "value")


class TestBodyItem(unittest.TestCase):

    def test_all_body_items_have_type(self):
        for cls in subclasses(BodyItem):
            if getattr(cls, "type", None) is None:
                raise AssertionError(f"{cls.__name__} has no type attribute")

    def test_id_without_parent(self):
        for cls in subclasses(BodyItem):
            if issubclass(cls, (If, Try)):
                assert_equal(cls().id, None)
            elif issubclass(cls, Message):
                assert_equal(cls().id, "m1")
            else:
                assert_equal(cls().id, "k1")

    def test_id_with_parent(self):
        for cls in subclasses(BodyItem):
            tc = ResultTestCase()
            tc.body = [cls(), cls(), cls()]
            if issubclass(cls, (If, Try)):
                assert_equal([item.id for item in tc.body], [None, None, None])
            elif cls is Message:
                pass
            elif issubclass(cls, Message):
                assert_equal([item.id for item in tc.body], ["t1-m1", "t1-m2", "t1-m3"])
            else:
                assert_equal([item.id for item in tc.body], ["t1-k1", "t1-k2", "t1-k3"])

    def test_id_with_parent_having_setup_and_teardown(self):
        tc = TestCase()
        assert_equal(tc.setup.config(name="S").id, "t1-k1")
        assert_equal(tc.teardown.config(name="T").id, "t1-k2")
        tc.body = [Keyword(), Keyword(), If(), Keyword()]
        assert_equal([item.id for item in tc.body], ["t1-k2", "t1-k3", None, "t1-k4"])
        assert_equal(tc.setup.id, "t1-k1")
        assert_equal(tc.teardown.id, "t1-k5")

    def test_id_when_item_not_in_parent(self):
        tc = TestCase(parent=TestSuite(parent=TestSuite()))
        assert_equal(tc.id, "s1-s1-t1")
        assert_equal(Keyword(parent=tc).id, "s1-s1-t1-k1")
        tc.body.create_keyword()
        tc.body.create_if().body.create_branch()
        assert_equal(Keyword(parent=tc).id, "s1-s1-t1-k3")

    def test_id_with_if(self):
        tc = TestCase()
        root = tc.body.create_if()
        assert_equal(root.id, None)
        branch = root.body.create_branch()
        assert_equal(branch.id, "t1-k1")
        assert_equal(branch.body.create_keyword().id, "t1-k1-k1")
        assert_equal(branch.body.create_keyword().id, "t1-k1-k2")
        branch = root.body.create_branch()
        assert_equal(branch.id, "t1-k2")
        assert_equal(branch.body.create_keyword().id, "t1-k2-k1")
        assert_equal(branch.body.create_keyword().id, "t1-k2-k2")
        assert_equal(tc.body.create_keyword().id, "t1-k3")

    def test_id_with_try(self):
        tc = TestCase()
        root = tc.body.create_try()
        assert_equal(root.id, None)
        branch = root.body.create_branch()
        assert_equal(branch.id, "t1-k1")
        assert_equal(branch.body.create_keyword().id, "t1-k1-k1")
        assert_equal(branch.body.create_keyword().id, "t1-k1-k2")
        branch = root.body.create_branch()
        assert_equal(branch.id, "t1-k2")
        assert_equal(branch.body.create_keyword().id, "t1-k2-k1")
        assert_equal(branch.body.create_keyword().id, "t1-k2-k2")
        assert_equal(tc.body.create_keyword().id, "t1-k3")

    def test_id_with_if_and_try(self):
        tc = TestCase()
        # IF
        root = tc.body.create_if()
        assert_equal(root.id, None)
        branch = root.body.create_branch()
        assert_equal(branch.id, "t1-k1")
        assert_equal(branch.body.create_keyword().id, "t1-k1-k1")
        assert_equal(branch.body.create_keyword().id, "t1-k1-k2")
        branch = root.body.create_branch()
        assert_equal(branch.id, "t1-k2")
        assert_equal(branch.body.create_keyword().id, "t1-k2-k1")
        assert_equal(branch.body.create_keyword().id, "t1-k2-k2")
        assert_equal(tc.body.create_keyword().id, "t1-k3")
        # TRY
        root = tc.body.create_try()
        assert_equal(root.id, None)
        branch = root.body.create_branch()
        assert_equal(branch.id, "t1-k4")
        assert_equal(branch.body.create_keyword().id, "t1-k4-k1")
        assert_equal(branch.body.create_keyword().id, "t1-k4-k2")
        branch = root.body.create_branch()
        assert_equal(branch.id, "t1-k5")
        assert_equal(branch.body.create_keyword().id, "t1-k5-k1")
        assert_equal(branch.body.create_keyword().id, "t1-k5-k2")
        assert_equal(tc.body.create_keyword().id, "t1-k6")
        # IF again
        root = tc.body.create_if()
        assert_equal(root.id, None)
        branch = root.body.create_branch()
        assert_equal(branch.id, "t1-k7")
        assert_equal(branch.body.create_keyword().id, "t1-k7-k1")
        assert_equal(branch.body.create_keyword().id, "t1-k7-k2")
        branch = root.body.create_branch()
        assert_equal(branch.id, "t1-k8")
        assert_equal(branch.body.create_keyword().id, "t1-k8-k1")
        assert_equal(branch.body.create_keyword().id, "t1-k8-k2")
        assert_equal(tc.body.create_keyword().id, "t1-k9")


if __name__ == "__main__":
    unittest.main()
