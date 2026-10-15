import unittest

from robot.model.metadata import Metadata
from robot.utils.asserts import assert_equal


class TestMetadata(unittest.TestCase):

    def test_normalization(self):
        md = Metadata(
            [
                ("m1", "xxx"),
                ("M2", "xxx"),
                ("m_3", "xxx"),
                ("M1", "YYY"),
                ("M 3", "YYY"),
            ]
        )
        assert_equal(dict(md), {"m1": "YYY", "M2": "xxx", "m_3": "YYY"})

    def test_str(self):
        assert_equal(str(Metadata()), "{}")
        d = {"a": 1, "B": "two", "ä": "neljä"}
        assert_equal(str(Metadata(d)), "{a: 1, B: two, ä: neljä}")

    def test_non_string_items(self):
        md = Metadata([("number", 42), ("boolean", True), (1, "one")])
        assert_equal(md["number"], "42")
        assert_equal(md["boolean"], "True")
        assert_equal(md["1"], "one")
        md["number"] = 1.0
        md["boolean"] = False
        md["new"] = []
        md[True] = ""
        assert_equal(md["number"], "1.0")
        assert_equal(md["boolean"], "False")
        assert_equal(md["new"], "[]")
        assert_equal(md["True"], "")
        md.setdefault("number", 99)
        md.setdefault("setdefault", 99)
        assert_equal(md["number"], "1.0")
        assert_equal(md["setdefault"], "99")

    def test_set(self):
        md = Metadata()
        md.set("Owner", "QA Team")
        assert_equal(dict(md), {"Owner": "QA Team"})
        md.set("Owner", "Dev Team")
        assert_equal(dict(md), {"Owner": "Dev Team"})
        md.set("Empty")
        assert_equal(dict(md), {"Owner": "Dev Team", "Empty": ""})

    def test_set_removes_using_hyphen(self):
        md = Metadata({"Owner": "QA Team", "Priority": "Normal"})
        md.set("-Owner")
        assert_equal(dict(md), {"Priority": "Normal"})

    def test_set_removal_is_normalized(self):
        md = Metadata({"Owner": "QA Team"})
        md.set("-o_w n e r")
        assert_equal(dict(md), {})

    def test_set_removing_non_existing_is_no_operation(self):
        md = Metadata({"Owner": "QA Team"})
        md.set("-Nonex")
        assert_equal(dict(md), {"Owner": "QA Team"})

    def test_set_does_not_support_patterns(self):
        md = Metadata({"Priority": "Normal"})
        md.set("-Priorit*")
        assert_equal(dict(md), {"Priority": "Normal"})

    def test_set_with_escaped_hyphen_is_not_removal(self):
        md = Metadata({"Owner": "QA Team"})
        md.set("\\-Owner", "literal")
        assert_equal(dict(md), {"Owner": "QA Team", "\\-Owner": "literal"})

    def test_set_removal_resets_name_spelling(self):
        md = Metadata({"Owner": "QA Team"})
        md.set("owner", "Dev Team")
        assert_equal(dict(md), {"Owner": "Dev Team"})
        md.set("-OWNER")
        md.set("owner", "New Team")
        assert_equal(dict(md), {"owner": "New Team"})


if __name__ == "__main__":
    unittest.main()
