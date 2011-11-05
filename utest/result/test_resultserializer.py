from itertools import chain
import unittest
from StringIO import StringIO
from xml.etree.ElementTree import XML
from xml.etree.ElementTree import tostring
from robot.reporting.outputparser import OutputParser

from robot.result.builders import ResultFromXML
from robot.result.serializer import RebotXMLWriter
from robot.result.datamodel import DatamodelVisitor
from robot.utils.asserts import assert_equals

from test_resultbuilder import GOLDEN_XML, GOLDEN_XML_TWICE


class TestResultSerializer(unittest.TestCase):

    def test_single_result_serialization(self):
        output = StringIO()
        ResultFromXML(StringIO(GOLDEN_XML)).visit(RebotXMLWriter(output))
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
        result.visit(RebotXMLWriter(output))
        self._assert_xml_content(self._xml_lines(output.getvalue()),
                                 self._xml_lines(GOLDEN_XML_TWICE))

class TestResultJSONSerializer(unittest.TestCase):

    def setUp(self):
        output_parser = OutputParser()
        output_parser._parse_fileobj(StringIO(GOLDEN_XML))
        self._expected = output_parser._get_data_model()._robot_data
        visitor = DatamodelVisitor(ResultFromXML(StringIO(GOLDEN_XML)))
        self._datamodel = visitor.datamodel

    def test_datamodel_suite(self):
        self._equals('suite')

    def test_datamodel_basemillis(self):
        self._equals('baseMillis')

    def test_datamodel_strings(self):
        self._equals('strings')

    def _equals(self, key):
        if isinstance(self._expected[key], list):
            for exp, act in zip(self._expected[key], self._datamodel[key]):
                assert_equals(exp, act)
        else:
            assert_equals(self._expected[key], self._datamodel[key])


if __name__ == '__main__':
    unittest.main()
