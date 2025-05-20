ROBOT_LISTENER_API_VERSION = 3


def startTest(data, result):
    result.message = f"[START] [original] {data.name} [resolved] {result.name}"


def end_test(data, result):
    result.message += f"\n[END] [original] {data.name} [resolved] {result.name}"
