import platform

from robot.api.types import Secret

# We assume that prompt is PS1='\u@\h \W \$ '
HOST = "localhost"
USERNAME = "test"
PASSWORD = "test"
PROMPT = "$ "
FULL_PROMPT = f"{USERNAME}@{platform.uname()[1]} ~ $ "
PROMPT_START = f"{USERNAME}@"
HOME = f"/home/{USERNAME}"

# Secret variables for testing
SECRET_USERNAME = Secret(USERNAME)
SECRET_PASSWORD = Secret(PASSWORD)
SECRET_COMMAND = Secret("echo secret-test-value")
SECRET_TEXT = Secret("secret-text-123")
