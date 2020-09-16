from robot.running.model import Keyword

ROBOT_LISTENER_API_VERSION=3

def start_suite(data, result):
    print(repr(data))

def start_keyword(data: Keyword, result):
    print(data.name, data.lineno, dir(data))
    data.name = "Comment"
    data.keywords.create(name="Fail", args=("Jotain BLAAH MI",))


def _end_keyword(data, result):
    print(type(data))
    print(type(result))
