import platform

# We assume that prompt is PS1='\u@\h \W \$ '
HOST = "localhost"
USERNAME = "test"
PASSWORD = "test"
PROMPT = "$ "
FULL_PROMPT = f"{USERNAME}@{platform.uname()[1]} ~ $ "
PROMPT_START = f"{USERNAME}@"
HOME = f"/home/{USERNAME}"
