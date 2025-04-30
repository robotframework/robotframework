from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

run_keyword = BuiltIn().run_keyword


def start_keyword(data, result):
    message = result.args[0]
    if message.startswith("Limited "):
        limit = int(message.split()[1]) - 1
        if limit > 0:
            run_keyword("Log", f"Limited {limit} (by start_keyword)")
    if message == "Unlimited in start_keyword":
        run_keyword("Log", message)


def end_keyword(data, result):
    message = result.args[0]
    if message.startswith("Limited "):
        limit = int(message.split()[1]) - 1
        if limit > 0:
            run_keyword("Log", f"Limited {limit} (by end_keyword)")
    if message == "Unlimited in end_keyword":
        run_keyword("Log", message)


def log_message(msg):
    if msg.message.startswith("Limited "):
        limit = int(msg.message.split()[1]) - 1
        if limit > 0:
            logger.info(f"Limited {limit} (by log_message)")
    if msg.message == "Unlimited in log_message":
        logger.info(msg.message)
