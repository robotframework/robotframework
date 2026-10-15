import unittest

from robot.running import TestCase
from robot.running.builder.settings import FileSettings, InitFileSettings, TestDefaults
from robot.utils.asserts import assert_equal


class TestTestDefaultsMetadata(unittest.TestCase):

    def test_no_metadata_by_default(self):
        assert_equal(dict(TestDefaults().metadata), {})

    def test_metadata_can_be_set_in_constructor(self):
        defaults = TestDefaults(metadata={"Owner": "QA Team"})
        assert_equal(dict(defaults.metadata), {"Owner": "QA Team"})

    def test_metadata_is_inherited_from_parent(self):
        parent = TestDefaults(metadata={"Owner": "QA Team", "Priority": "Normal"})
        child = TestDefaults(parent)
        assert_equal(dict(child.metadata), {"Owner": "QA Team", "Priority": "Normal"})

    def test_child_overrides_and_adds(self):
        parent = TestDefaults(metadata={"Owner": "QA Team", "Priority": "Normal"})
        child = TestDefaults(parent)
        child.metadata.set("Priority", "High")
        child.metadata.set("Issue", "4409")
        assert_equal(
            dict(child.metadata),
            {"Owner": "QA Team", "Priority": "High", "Issue": "4409"},
        )
        assert_equal(dict(parent.metadata), {"Owner": "QA Team", "Priority": "Normal"})

    def test_child_removes_item_set_by_parent(self):
        parent = TestDefaults(metadata={"Owner": "QA Team", "Priority": "Normal"})
        child = TestDefaults(parent)
        child.metadata.set("-Owner")
        assert_equal(dict(child.metadata), {"Priority": "Normal"})
        assert_equal(dict(parent.metadata), {"Owner": "QA Team", "Priority": "Normal"})

    def test_removal_is_inherited_by_grandchild(self):
        grand = TestDefaults(metadata={"Owner": "QA Team", "Priority": "Normal"})
        parent = TestDefaults(grand)
        parent.metadata.set("-Owner")
        child = TestDefaults(parent)
        assert_equal(dict(child.metadata), {"Priority": "Normal"})

    def test_set_to_does_not_override_own_metadata(self):
        defaults = TestDefaults(metadata={"Owner": "QA Team", "Priority": "Normal"})
        test = TestCase(metadata={"Priority": "Critical"})
        defaults.set_to(test)
        assert_equal(dict(test.metadata), {"Priority": "Critical", "Owner": "QA Team"})


class TestFileSettingsMetadata(unittest.TestCase):

    def test_defaults_are_inherited(self):
        defaults = TestDefaults(metadata={"Owner": "QA Team"})
        assert_equal(dict(FileSettings(defaults).test_metadata), {"Owner": "QA Team"})

    def test_suite_file_does_not_affect_siblings(self):
        defaults = TestDefaults(metadata={"Owner": "QA Team"})
        first = FileSettings(defaults)
        first.test_metadata.set("Suite File", "first")
        first.test_metadata.set("-Owner")
        second = FileSettings(defaults)
        assert_equal(dict(first.test_metadata), {"Suite File": "first"})
        assert_equal(dict(second.test_metadata), {"Owner": "QA Team"})
        assert_equal(dict(defaults.metadata), {"Owner": "QA Team"})

    def test_init_file_settings_write_to_shared_defaults(self):
        parent = TestDefaults(metadata={"Owner": "QA Team"})
        defaults = TestDefaults(parent)
        settings = InitFileSettings(defaults)
        settings.test_metadata.set("Priority", "High")
        settings.test_metadata.set("-Owner")
        assert_equal(dict(defaults.metadata), {"Priority": "High"})
        assert_equal(dict(settings.test_metadata), {"Priority": "High"})


if __name__ == "__main__":
    unittest.main()
