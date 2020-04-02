ROBOT_LISTENER_API_VERSION = 3


def startTest(data, result):
    result.message = '[START] [original] %s [resolved] %s' % (data.name, result.name)


def end_test(data, result):
    result.message += '\n[END] [original] %s [resolved] %s' % (data.name, result.name)
