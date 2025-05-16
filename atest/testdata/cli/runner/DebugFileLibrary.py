from pathlib import Path

from robot.api import logger


def log_and_validate_message_is_in_debug_file(debug_file: Path):
    logger.info("Hello, debug file!")
    content = debug_file.read_text(encoding="UTF-8")
    if "INFO - Hello, debug file!" not in content:
        raise AssertionError(
            f"Logged message 'Hello, debug file!' not found from "
            f"the debug file:\n\n{content}"
        )
    if "DEBUG - Test timeout 10 seconds active." not in content:
        raise AssertionError("Timeouts are not active!")
