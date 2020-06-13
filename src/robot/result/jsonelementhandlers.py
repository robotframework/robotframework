

class JsonElementHandler(object):

    def __init__(self, execution_result):
        self._result = execution_result

    def parse(self, json_data):
        parse_robot(json_data, self._result)


def parse_robot(root_element, result):
    generator = root_element.get('generator', 'unknown').split()[0].upper()
    result.generated_by_robot = generator == 'ROBOT'
    if result.rpa is None:
        result.rpa = root_element.get('rpa', 'false') == 'true'

    parse_root_suite(root_element.get('suite', None), result)
    for element in root_element.get('errors', []):
        parse_message(element, result.errors)


def parse_root_suite(suite_element, result):
    result.suite.name = suite_element.get('name', '')
    result.suite.source = suite_element.get('source')
    result.suite.rpa = result.rpa
    result.suite.doc = suite_element.get('doc', '')

    for suite in suite_element.get('suites', []):
        parse_suite(suite, result.suite)
    for element in suite_element.get('tests', []):
        parse_test(element, result.suite)
    for element in suite_element.get('kw', []):
        parse_keyword(element, result.suite)

    parse_metadata(suite_element.get('metadata', None), result.suite)
    parse_status(suite_element.get('status', None), result.suite, "suite")


def parse_suite(suite_element, result):
    if not suite_element:
        return
    try:
        suite = result.suites.create(name=suite_element.get('name', ''),
                                     source=suite_element.get('source', ''),
                                     rpa=result.rpa)
    except Exception as e:
        print(e)
    suite.doc = suite_element.get('doc', '')
    parse_metadata(suite_element.get('metadata', None), suite)
    parse_status(suite_element.get('status', None), suite, "suite")
    for element in suite_element.get('suites', []):
        parse_suite(element, suite)
    for element in suite_element.get('tests', []):
        parse_test(element, suite)
    for element in suite_element.get('kw', []):
        parse_keyword(element, suite)


def parse_metadata(metadata_element, result):
    if not metadata_element:
        return
    for key, value in metadata_element.items():
        result.metadata[key] = value


def parse_status(status_element, result, type):
    if not status_element:
        return
    result.starttime = status_element.get('starttime', None)
    result.endtime = status_element.get('endtime', None)
    if type != "suite":
        result.status = status_element.get('status', 'FAIL')
    if type != "keyword" or result.type == result.TEARDOWN_TYPE:
        result.message = status_element.get('message', None)


def parse_test(test_element, result):
    if not test_element:
        return
    test = result.tests.create(name=test_element.get('name', ''))
    test.doc = test_element.get('doc', '')
    test.timeout = test_element.get('timeout', None)
    for tag in test_element.get('tags', []):
        test.tags.add(tag)
    parse_status(test_element.get('status', None), test, "test")
    for element in test_element.get('kw', []):
        parse_keyword(element, test)


def parse_keyword(keyword_element, result):
    if not keyword_element:
        return
    keyword = result.keywords.create(kwname=keyword_element.get('name', ''),
                                     libname=keyword_element.get('lib', ''),
                                     type=keyword_element.get('type', 'kw'))
    keyword.doc = keyword_element.get('doc', '')
    keyword.timeout = keyword_element.get('timeout', None)
    for arg in keyword_element.get('args', []):
        if not keyword.args:
            keyword.args = list()
        keyword.args.append(arg)
    for assign in keyword_element.get('assign', []):
        keyword.assign += assign
    for tag in keyword_element.get('tags', []):
        keyword_element.tags.add(tag)
    for element in keyword_element.get('msgs', []):
        parse_message(element, keyword)
    for element in keyword_element.get('kw', []):
        parse_keyword(element, keyword)
    parse_status(keyword_element.get('status', None), keyword, "keyword")


def parse_message(message_element, result):
    result.messages.create(message_element.get('msg', ''),
                           message_element.get('level', 'INFO'),
                           message_element.get('html', False),
                           message_element.get('timestamp', None))
