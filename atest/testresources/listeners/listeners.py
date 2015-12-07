import os

from robot.libraries.BuiltIn import BuiltIn


class ListenSome:
    ROBOT_LISTENER_API_VERSION = '2'

    def __init__(self):
        outpath = os.path.join(os.getenv('TEMPDIR'), 'listen_some.txt')
        self.outfile = open(outpath, 'w')

    def startTest(self, name, attrs):
        self.outfile.write(name + '\n')

    def endSuite(self, name, attrs):
        self.outfile.write(attrs['statistics'] + '\n')

    def close(self):
        self.outfile.close()


class WithArgs(object):
    ROBOT_LISTENER_API_VERSION = '2'

    def __init__(self, arg1, arg2='default'):
        outpath = os.path.join(os.getenv('TEMPDIR'), 'listener_with_args.txt')
        outfile = open(outpath, 'a')
        outfile.write("I got arguments '%s' and '%s'\n" % (arg1, arg2))
        outfile.close()


class SuiteAndTestCounts(object):
    ROBOT_LISTENER_API_VERSION = '2'
    exp_data = {
        'Subsuites & Subsuites2': ([], ['Subsuites', 'Subsuites2'], 5),
        'Subsuites':              ([], ['Sub1', 'Sub2'], 2),
        'Sub1':                   (['SubSuite1 First'], [], 1),
        'Sub2':                   (['SubSuite2 First'], [], 1),
        'Subsuites2':             ([], ['Sub.Suite.4', 'Subsuite3'], 3),
        'Subsuite3':              (['SubSuite3 First', 'SubSuite3 Second'], [], 2),
        'Sub.Suite.4':            (['Test From Sub Suite 4'], [], 1)
        }

    def start_suite(self, name, attrs):
        data = attrs['tests'], attrs['suites'], attrs['totaltests']
        if data != self.exp_data[name]:
            raise RuntimeError('Wrong tests or suites in %s, %s != %s' %
                               (name, self.exp_data[name], data))


class KeywordType(object):
    ROBOT_LISTENER_API_VERSION = '2'

    def start_keyword(self, name, attrs):
        expected = self._get_expected_kw_type(name, attrs['args'])
        if attrs['type'] != expected:
            raise RuntimeError("Wrong keyword type '%s', expected '%s'."
                               % (attrs['type'], expected))

    def _get_expected_kw_type(self, name, args):
        if 'IN' in name:
            return 'For'
        if '=' in name:
            return 'For Item'
        expected = args[0] if name.startswith('BuiltIn.') else name
        return {'Suite Setup': 'Setup', 'Suite Teardown': 'Teardown',
                'Test Setup': 'Setup', 'Test Teardown': 'Teardown',
                'Keyword Teardown': 'Teardown'}.get(expected, 'Keyword')

    end_keyword = start_keyword


class KeywordExecutingListener(object):
    ROBOT_LISTENER_API_VERSION = '2'

    def start_suite(self, name, attrs):
        self._start(name)

    def end_suite(self, name, attrs):
        self._end(name)

    def start_test(self, name, attrs):
        self._start(name)

    def end_test(self, name, attrs):
        self._end(name)

    def _start(self, name):
        self._run_keyword('Start %s' % name)

    def _end(self, name):
        self._run_keyword('End %s' % name)

    def _run_keyword(self, arg):
        BuiltIn().run_keyword('Log', arg)


class SuiteSource(object):
    ROBOT_LISTENER_API_VERSION = '2'

    def __init__(self):
        self._started = 0
        self._ended = 0

    def start_suite(self, name, attrs):
        self._started += 1
        self._test_source(name, attrs['source'])

    def end_suite(self, name, attrs):
        self._ended += 1
        self._test_source(name, attrs['source'])

    def _test_source(self, suite, source):
        default = os.path.isfile
        verifier = {'Root': lambda source: source == '',
                    'Subsuites': os.path.isdir}.get(suite, default)
        if (source and not os.path.isabs(source)) or not verifier(source):
            raise AssertionError("Suite '%s' has wrong source '%s'."
                                 % (suite, source))

    def close(self):
        if not (self._started == self._ended == 5):
            raise AssertionError("Wrong number of started (%d) or ended (%d) "
                                 "suites. Expected 5."
                                 % (self._started, self._ended))


class Messages(object):
    ROBOT_LISTENER_API_VERSION = '2'

    def __init__(self, path):
        self.output = open(path, 'w')

    def log_message(self, msg):
        self.output.write('%s: %s\n' % (msg['level'], msg['message']))

    def close(self):
        self.output.close()
