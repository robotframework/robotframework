ROBOT_LISTENER_API_VERSION = 2


def startTest(name, info):
    print('[START] [original] %s [resolved] %s' % (info['originalname'], name))


def end_test(name, info):
    print('[END] [original] %s [resolved] %s' % (info['originalname'], name))
