import StringIO
import unittest
import os

from robot.parsing.model import TestCaseFile, ResourceFile
from robot.parsing.populators import FromFilePopulator
from robot.parsing.txtreader import TxtReader
from robot.utils.asserts import assert_equals
from robot.writer.serializer import Serializer, SerializationContext

from golden import (GOLDEN_TXT_RESOURCE, GOLDEN_TXT_TESTCASE_FILE,
                    GOLDEN_TXT_PIPE_RESOURCE, GOLDEN_TXT_PIPE_TESTCASE_FILE,
                    GOLDEN_TSV_RESOURCE, GOLDEN_TSV_TESTCASE_FILE,
                    GOLDEN_HTML_TESTCASE_FILE)


def _create_testcase_file():
    tcf = TestCaseFile()
    TxtReader().read(StringIO.StringIO(GOLDEN_TXT_TESTCASE_FILE),
                     FromFilePopulator(tcf))
    return tcf

def _create_resource_file():
    res = ResourceFile()
    TxtReader().read(StringIO.StringIO(GOLDEN_TXT_RESOURCE),
                    FromFilePopulator(res))
    return res

TESTCASE_FILE = _create_testcase_file()
RESOURCE_FILE = _create_resource_file()


class _SerializerTest(unittest.TestCase):
    _serializer = None

    def _serialize(self, datafile, extension, pipe_separated=False,
                   line_separator=os.linesep):
        datafile.source = '/not/really/here.' + extension
        output = StringIO.StringIO()
        Serializer().serialize(datafile, output=output,
                               pipe_separated=pipe_separated,
                               line_separator=line_separator)
        return output.getvalue()

    def _assert_serialization_with_different_line_separators(self, datafile,
                                                             expected):
        for linesep in '\n', '\r\n':
            output = self._serializer(datafile, line_separator=linesep)
            self._assert_result(output, expected, linesep)

    def _assert_serialization(self, datafile, expected):
        self._assert_result(self._serializer(datafile), expected)

    def _assert_result(self, result, expected, linesep=os.linesep):
        for line1, line2 in zip(result.split(linesep), expected.split('\n')):
            assert_equals(line1, line2)


class TestTxtSerialization(_SerializerTest):

    def _serializer(self, datafile, line_separator=os.linesep):
        return self._serialize(datafile, 'txt', line_separator=line_separator)

    def test_serializing_txt_resource_file(self):
        self._assert_serialization(RESOURCE_FILE, GOLDEN_TXT_RESOURCE)

    def test_serializing_txt_test_case_file(self):
        self._assert_serialization(TESTCASE_FILE, GOLDEN_TXT_TESTCASE_FILE)

    def test_serializing_with_different_line_separators(self):
        files = TESTCASE_FILE, GOLDEN_TXT_TESTCASE_FILE
        self._assert_serialization_with_different_line_separators(*files)


class TestPipeTxtSerialization(_SerializerTest):

    def _serializer(self, datafile, line_separator=os.linesep):
        return self._serialize(datafile, 'txt', pipe_separated=True,
                               line_separator=line_separator)

    def test_serializer_with_txt_resource_file(self):
        self._assert_serialization(RESOURCE_FILE, GOLDEN_TXT_PIPE_RESOURCE)

    def test_serializer_with_txt_test_case_file(self):
        self._assert_serialization(TESTCASE_FILE, GOLDEN_TXT_PIPE_TESTCASE_FILE)

    def test_serializer_with_different_line_separators(self):
        files = TESTCASE_FILE, GOLDEN_TXT_PIPE_TESTCASE_FILE
        self._assert_serialization_with_different_line_separators(*files)


class TestTsvSerialization(_SerializerTest):

    def _serializer(self, datafile, line_separator=os.linesep):
        return self._serialize(datafile, 'tsv', pipe_separated=True,
                               line_separator=line_separator)

    def test_serializing_resource_file(self):
        self._assert_serialization(RESOURCE_FILE, GOLDEN_TSV_RESOURCE)

    def test_serializing_testcase_file(self):
        self._assert_serialization(TESTCASE_FILE, GOLDEN_TSV_TESTCASE_FILE)

    def test_serializing_with_different_line_separators(self):
        files = TESTCASE_FILE, GOLDEN_TSV_TESTCASE_FILE
        self._assert_serialization_with_different_line_separators(*files)


class TestHTMLSerialization(_SerializerTest):

    def _serializer(self, datafile):
            return self._serialize(datafile, 'html')

    def test_serializer_with_html_testcase_file(self):
        self._assert_serialization(TESTCASE_FILE, GOLDEN_HTML_TESTCASE_FILE)


if __name__ == "__main__":
    unittest.main()
