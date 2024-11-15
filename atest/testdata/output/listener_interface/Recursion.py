from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn


run_keyword = BuiltIn().run_keyword


def log_message(msg):
    try:
        countdown = int(msg.message.split()[0]) - 1
    except ValueError:
        return
    if countdown > 0:
        logger.info(f'{countdown} (by log_message)')


def start_keyword(data, result):
    countdown = int(result.args[0].split()[0]) - 1
    if countdown > 0:
        run_keyword('Log', f'{countdown} (by start_keyword)')


def end_keyword(data, result):
    countdown = int(result.args[0].split()[0]) - 1
    if countdown > 0:
        run_keyword('Log', f'{countdown} (by end_keyword)')
