import unittest
from robot import utils
from robot.model.message import Message
from robot.output.loggerhelper import LEVELS
from robot.reporting.parsingcontext import Context
from robot.result.datamodel import DatamodelVisitor
from robot.result.jsondatamodelhandlers import _Handler
from robot.utils.asserts import assert_equals


class TestJsoning(unittest.TestCase, DatamodelVisitor):

    def setUp(self):
        self._elements = []
        self._context = Context()
        self._elements.append(_Handler(self._context))

    def test_html_message_to_json(self):
        message = Message(message='<b>Great danger!</b>',
                          level='WARN',
                          html=True,
                          timestamp='20121212 12:12:12.121')
        message.visit(self)
        self._verify_message(self.datamodel[0], message)

    def test_non_html_message_to_json(self):
        message = Message(message='This is an html mark --> <html>',
                          level='INFO',
                          html=False,
                          timestamp='19991211 12:12:12.821')
        message.visit(self)
        message.message = utils.html_escape(message.message)
        self._verify_message(self.datamodel[0], message)

    def _verify_message(self, message_json, message):
        assert_equals(message_json[0], self._context.timestamp(message.timestamp))
        assert_equals(message_json[1], LEVELS[message.level])
        assert_equals(message_json[2], self._context.get_id(message.message))


if __name__ == '__main__':
    unittest.main()
