import unittest
import os
from StringIO import StringIO
from xml.etree.ElementTree import XML
from xml.etree.ElementTree import tostring

from robot.result.builders import ResultFromXML
from robot.result.serializer import RebotXMLWriter
from robot.utils.pyxmlwriter import XmlWriter
from robot.utils.asserts import assert_equals

from test_resultbuilder import GOLDEN_XML, GOLDEN_XML_TWICE


class StreamXmlWriter(XmlWriter):

    def _create_output(self, output):
        return output

if os.name == 'java':
    from java.io import Writer
    from array import array
    from robot.utils.jyxmlwriter import XmlWriter

    class StreamXmlWriter(XmlWriter):

        def _create_output(self, output):
            return StreamOutputWriter(output)

    class StreamOutputWriter(Writer):

        def __init__(self, output):
            self._output = output

        def close(self):
            pass

        def flush(self):
            pass

        def write(self, value, offset=None, length=None):
            # There are 5 overloaded version of #write() in java.io.Writer,
            # the three that TransformHandler uses are handled below.
            self._output.write(self._content(value, offset, length))

        def _content(self, value, offset, length):
            if isinstance(value, array):
                return value[offset:offset+length].tostring()
            if isinstance(value, int):
                return unichr(value)
            return value


class TestableRebotXmlWriter(RebotXMLWriter):

    def _get_writer(self, output, generator):
        writer = StreamXmlWriter(output)
        writer.start('robot')
        return writer


class TestResultSerializer(unittest.TestCase):

    def _create_writer(self, output):
        return TestableRebotXmlWriter(output)

    def test_single_result_serialization(self):
        output = StringIO()
        ResultFromXML(StringIO(GOLDEN_XML)).visit(self._create_writer(output))
        self._assert_xml_content(self._xml_lines(output.getvalue()),
                                 self._xml_lines(GOLDEN_XML))

    def _xml_lines(self, text):
        return tostring(XML(text)).splitlines()

    def _assert_xml_content(self, actual, expected):
        assert_equals(len(actual), len(expected))
        for index, (act, exp) in enumerate(zip(actual, expected)[2:]):
            assert_equals(act, exp.strip(), 'Different values on line %d' % index)

    def test_combining_results(self):
        output = StringIO()
        result = ResultFromXML(StringIO(GOLDEN_XML), StringIO(GOLDEN_XML))
        result.visit(self._create_writer(output))
        self._assert_xml_content(self._xml_lines(output.getvalue()),
                                 self._xml_lines(GOLDEN_XML_TWICE))

if __name__ == '__main__':
    unittest.main()
