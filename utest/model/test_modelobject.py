import io
import json
import os
import pathlib
import unittest
import tempfile

from robot.errors import DataError
from robot.model.modelobject import ModelObject
from robot.utils import get_error_message
from robot.utils.asserts import assert_equal, assert_raises_with_msg


class Example(ModelObject):

    def __init__(self, a=None, b=None, c=None):
        self.a = a
        self.b = b
        self.c = c

    def __setattr__(self, name, value):
        if value == 'fail':
            raise AttributeError('Ooops!')
        self.__dict__[name] = value

    def to_dict(self):
        return self.__dict__


class TestRepr(unittest.TestCase):

    def test_default(self):
        assert_equal(repr(ModelObject()), 'robot.model.ModelObject()')

    def test_module_when_extending(self):
        assert_equal(repr(Example()), f'{__name__}.Example()')

    def test_repr_args(self):
        class X(ModelObject):
            repr_args = ('z', 'x')
            x, y, z = 1, 2, 3
        assert_equal(repr(X()), f'{__name__}.X(z=3, x=1)')


class TestConfig(unittest.TestCase):

    def test_basics(self):
        x = Example().config(a=1, c=3)
        assert_equal(x.a, 1)
        assert_equal(x.b, None)
        assert_equal(x.c, 3)

    def test_attributes_must_exist(self):
        assert_raises_with_msg(
            AttributeError,
            f"'{__name__}.Example' object does not have attribute 'bad'",
            Example().config, bad='attr'
        )

    def test_setting_attribute_fails(self):
        assert_raises_with_msg(
            AttributeError,
            "Setting attribute 'a' failed: Ooops!",
            Example().config, a='fail'
        )

    def test_preserve_tuples(self):
        x = Example(a=(1, 2, 3)).config(a=range(5))
        assert_equal(x.a, (0, 1, 2, 3, 4))

    def test_failure_converting_to_tuple(self):
        assert_raises_with_msg(
            TypeError,
            f"'{__name__}.Example' object attribute 'a' is 'tuple', got 'None'.",
            Example(a=()).config, a=None
        )


class TestFromDictAndJson(unittest.TestCase):

    def test_attributes(self):
        obj = Example.from_dict({'a': 1})
        assert_equal(obj.a, 1)
        assert_equal(obj.b, None)
        assert_equal(obj.c, None)
        obj = Example.from_json('{"a": null, "b": 42, "c": true}')
        assert_equal(obj.a, None)
        assert_equal(obj.b, 42)
        assert_equal(obj.c, True)

    def test_non_existing_attribute(self):
        assert_raises_with_msg(
            DataError,
            f"Creating '{__name__}.Example' object from dictionary failed: "
            f"'{__name__}.Example' object does not have attribute 'nonex'",
            Example.from_dict, {'nonex': 'attr'}
        )

    def test_setting_attribute_fails(self):
        assert_raises_with_msg(
            DataError,
            f"Creating '{__name__}.Example' object from dictionary failed: "
            f"Setting attribute 'a' failed: Ooops!",
            Example.from_dict, {'a': 'fail'}
        )

    def test_json_as_bytes(self):
        obj = Example.from_json(b'{"a": null, "b": 42}')
        assert_equal(obj.a, None)
        assert_equal(obj.b, 42)

    def test_json_as_open_file(self):
        obj = Example.from_json(io.StringIO('{"a": null, "b": 42, "c": "åäö"}'))
        assert_equal(obj.a, None)
        assert_equal(obj.b, 42)
        assert_equal(obj.c, "åäö")

    def test_json_as_path(self):
        with tempfile.NamedTemporaryFile('w', encoding='UTF-8', delete=False) as file:
            file.write('{"a": null, "b": 42, "c": "åäö"}')
        try:
            for path in file.name, pathlib.Path(file.name):
                obj = Example.from_json(path)
                assert_equal(obj.a, None)
                assert_equal(obj.b, 42)
                assert_equal(obj.c, "åäö")
        finally:
            os.remove(file.name)

    def test_invalid_json_type(self):
        error = self._get_json_load_error(None)
        assert_raises_with_msg(
            DataError,
            f"Loading JSON data failed: Invalid JSON data: {error}",
            ModelObject.from_json, None
        )

    def test_invalid_json_syntax(self):
        error = self._get_json_load_error('bad')
        assert_raises_with_msg(
            DataError,
            f"Loading JSON data failed: Invalid JSON data: {error}",
            ModelObject.from_json, 'bad'
        )

    def test_invalid_json_content(self):
        assert_raises_with_msg(
            DataError,
            "Loading JSON data failed: Expected dictionary, got list.",
            ModelObject.from_json, '["bad"]'
        )

    def _get_json_load_error(self, value):
        try:
            json.loads(value)
        except Exception:
            return get_error_message()


class TestToJson(unittest.TestCase):
    data = {'a': 1, 'b': [True, False], 'c': 'nön-äscii'}
    default_config = {'ensure_ascii': False, 'indent': 0, 'separators': (',', ':')}
    custom_config = {'indent': None, 'separators': (', ', ': '), 'ensure_ascii': True}

    def test_default_config(self):
        assert_equal(Example(**self.data).to_json(),
                     json.dumps(self.data, **self.default_config))

    def test_custom_config(self):
        assert_equal(Example(**self.data).to_json(**self.custom_config),
                     json.dumps(self.data, **self.custom_config))

    def test_write_to_open_file(self):
        for config in {}, self.custom_config:
            output = io.StringIO()
            Example(**self.data).to_json(output, **config)
            expected = json.dumps(self.data, **(config or self.default_config))
            assert_equal(output.getvalue(), expected)

    def test_write_to_path(self):
        with tempfile.NamedTemporaryFile(delete=False) as file:
            pass
        try:
            for path in file.name, pathlib.Path(file.name):
                for config in {}, self.custom_config:
                    Example(**self.data).to_json(path, **config)
                    expected = json.dumps(self.data, **(config or self.default_config))
                    with open(path, encoding='UTF-8') as file:
                        assert_equal(file.read(), expected)
        finally:
            os.remove(file.name)

    def test_invalid_output(self):
        assert_raises_with_msg(TypeError,
                               "Output should be None, path or open file, got integer.",
                               Example().to_json, 42)


if __name__ == '__main__':
    unittest.main()
