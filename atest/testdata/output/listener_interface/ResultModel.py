from pathlib import Path

from robot.api import logger
from robot.api.interfaces import ListenerV3


class ResultModel(ListenerV3):

    def __init__(self, model_file: Path):
        self.model_file = model_file
        self.item_stack = []

    def start_suite(self, data, result):
        self.item_stack.append([])

    def end_suite(self, data, result):
        self.item_stack.pop()

    def start_test(self, data, result):
        self.item_stack.append([])
        logger.info('Starting TEST')

    def end_test(self, data, result):
        logger.info('Ending TEST')
        self._verify_body(result)
        result.to_json(self.model_file)

    def start_body_item(self, data, result):
        self.item_stack[-1].append(result)
        self.item_stack.append([])
        logger.info(f'Starting {data.type}')

    def end_body_item(self, data, result):
        logger.info(f'Ending {data.type}')
        self._verify_body(result)

    def log_message(self, message):
        if message.message == 'Remove me!':
            message.message = None
        else:
            self.item_stack[-1].append(message)

    def _verify_body(self, result):
        actual = list(result.body)
        expected = self.item_stack.pop()
        if actual != expected:
            raise AssertionError(f"Body of {result} was not expected.\n"
                                 f"Got     : {actual}\nExpected: {expected}")
