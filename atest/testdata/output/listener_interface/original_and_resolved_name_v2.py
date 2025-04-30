ROBOT_LISTENER_API_VERSION = 2


def startTest(name, info):
    print(f"[START] [original] {info['originalname']} [resolved] {name}")


def end_test(name, info):
    print(f"[END] [original] {info['originalname']} [resolved] {name}")
