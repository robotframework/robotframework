import os

from robot.libraries.BuiltIn import BuiltIn


class ListenSome:

    def __init__(self):
        outpath = os.path.join(os.getenv('TEMPDIR'), 'listen_some.txt')
        self.outfile = open(outpath, 'w')

    def startTest(self, data, result):
        self.outfile.write(data.name + '\n')

    def endSuite(self, data, result):
        self.outfile.write(result.stat_message + '\n')

    def close(self):
        self.outfile.close()


class WithArgs:
    ROBOT_LISTENER_API_VERSION = '3'

    def __init__(self, arg1, arg2='default'):
        outpath = os.path.join(os.getenv('TEMPDIR'), 'listener_with_args.txt')
        with open(outpath, 'a') as outfile:
            outfile.write("I got arguments '%s' and '%s'\n" % (arg1, arg2))


class WithArgConversion:
    ROBOT_LISTENER_API_VERSION = '2'

    def __init__(self, integer: int, boolean=False):
        assert integer == 42
        assert boolean is True


class SuiteAndTestCounts:
    ROBOT_LISTENER_API_VERSION = '2'
    exp_data = {
        "Subsuites & Custom name for 📂 'subsuites2'":
            ([], ['Subsuites', "Custom name for 📂 'subsuites2'"], 5),
        'Subsuites':
            ([], ['Sub1', 'Sub2'], 2),
        'Sub1':
            (['SubSuite1 First'], [], 1),
        'Sub2':
            (['SubSuite2 First'], [], 1),
        "Custom name for 📂 'subsuites2'":
            ([], ['Sub.Suite.4', "Custom name for 📜 'subsuite3.robot'"], 3),
        "Custom name for 📜 'subsuite3.robot'":
            (['SubSuite3 First', 'SubSuite3 Second'], [], 2),
        'Sub.Suite.4':
            (['Test From Sub Suite 4'], [], 1)
    }

    def start_suite(self, name, attrs):
        data = attrs['tests'], attrs['suites'], attrs['totaltests']
        if data != self.exp_data[name]:
            raise AssertionError('Wrong tests or suites in %s: %s != %s.'
                                 % (name, self.exp_data[name], data))


class KeywordType:
    ROBOT_LISTENER_API_VERSION = '2'

    def start_keyword(self, name, attrs):
        expected = self._get_expected_type(**attrs)
        if attrs['type'] != expected:
            raise AssertionError("Wrong keyword type '%s', expected '%s'."
                                 % (attrs['type'], expected))

    def _get_expected_type(self, kwname, libname, args, source, lineno, **ignore):
        if kwname.startswith(('${x}    ', '@{finnish}    ')):
            return 'VAR'
        if ' IN ' in kwname:
            return 'FOR'
        if ' = ' in kwname:
            return 'ITERATION'
        if not args:
            if "'${x}' == 'wrong'" in kwname or '${i} == 9' in kwname:
                return 'IF'
            if "'${x}' == 'value'" in kwname:
                return 'ELSE IF'
            if kwname == '':
                source = os.path.basename(source)
                if source == 'for_loops.robot':
                    return 'BREAK' if lineno == 13 else 'CONTINUE'
                return 'ELSE'
        expected = args[0] if libname == 'BuiltIn' else kwname
        return {'Suite Setup': 'SETUP', 'Suite Teardown': 'TEARDOWN',
                'Test Setup': 'SETUP', 'Test Teardown': 'TEARDOWN',
                'Keyword Teardown': 'TEARDOWN'}.get(expected, 'KEYWORD')

    end_keyword = start_keyword


class KeywordStatus:
    ROBOT_LISTENER_API_VERSION = '2'

    def start_keyword(self, name, attrs):
        self._validate_status(attrs, 'NOT SET')

    def end_keyword(self, name, attrs):
        run_status = 'FAIL' if attrs['kwname'] == 'Fail' else 'PASS'
        self._validate_status(attrs, run_status)

    def _validate_status(self, attrs, run_status):
        expected = 'NOT RUN' if self._not_run(attrs) else run_status
        if attrs['status'] != expected:
            raise AssertionError('Wrong keyword status %s, expected %s.'
                                 % (attrs['status'], expected))

    def _not_run(self, attrs):
        return attrs['type'] in ('IF', 'ELSE') or attrs['args'] == ['not going here']


class KeywordExecutingListener:
    ROBOT_LISTENER_API_VERSION = '2'

    def start_test(self, name, attrs):
        self._run_keyword('Start %s' % name)

    def end_test(self, name, attrs):
        self._run_keyword('End %s' % name)

    def _run_keyword(self, arg):
        BuiltIn().run_keyword('Log', arg)


class SuiteSource:
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


class Messages:
    ROBOT_LISTENER_API_VERSION = '2'

    def __init__(self, path):
        self.output = open(path, 'w')

    def log_message(self, msg):
        self.output.write('%s: %s\n' % (msg['level'], msg['message']))

    def close(self):
        self.output.close()
