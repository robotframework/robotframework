import re
from os.path import abspath, dirname, join, normpath
import unittest
from pathlib import Path

from robot.conf.settings import _BaseSettings, RobotSettings, RebotSettings
from robot.errors import DataError
from robot.utils import WINDOWS
from robot.utils.asserts import assert_equal, assert_true


class SettingWrapper(_BaseSettings):

    def __init__(self):
        pass


class TestRobotAndRebotSettings(unittest.TestCase):

    def test_robot_and_rebot_settings_are_independent_1(self):
        # https://github.com/robotframework/robotframework/issues/881
        orig_opts = RobotSettings()._opts
        RebotSettings()
        assert_equal(RobotSettings()._opts, orig_opts)

    def test_robot_and_rebot_settings_are_independent_2(self):
        # https://github.com/robotframework/robotframework/pull/2438
        rebot = RebotSettings()
        assert_equal(rebot['TestNames'], [])
        robot = RobotSettings()
        robot['TestNames'].extend(['test1', 'test2'])
        assert_equal(rebot['TestNames'], [])

    def test_robot_settings_are_independent(self):
        settings1 = RobotSettings()
        assert_equal(settings1['Include'], [])
        settings2 = RobotSettings()
        settings2['Include'].append('tag')
        assert_equal(settings1['Include'], [])

    def test_extra_options(self):
        assert_equal(RobotSettings(name='My Name')['Name'], 'My Name')
        assert_equal(RobotSettings({'name': 'Override'}, name='Set')['Name'],'Set')

    def test_multi_options_as_single_string(self):
        assert_equal(RobotSettings({'test': 'one'})['TestNames'], ['one'])
        assert_equal(RebotSettings({'exclude': 'two'})['Exclude'], ['two'])

    def test_output_files(self):
        for name in 'Output.xml', 'Report.html', 'Log.html', 'XUnit.xml', 'DebugFile.txt':
            name, ext = name.split('.')
            expected = Path(f'test.{ext}').absolute()
            attr = (name[:-4] if name.endswith('File') else name).lower()
            for value in 'test', Path('test'):
                settings = RobotSettings({name.lower(): value})
                assert_equal(settings[name], expected)
                if hasattr(settings, attr):
                    assert_equal(getattr(settings, attr), expected)

    def test_output_files_with_timestamps(self):
        for name in 'Output.xml', 'Report.html', 'Log.html', 'XUnit.xml', 'DebugFile.txt':
            name, ext = name.split('.')
            for value in 'test', Path('test'):
                path = RobotSettings({name.lower(): value,
                                      'timestampoutputs': True})[name]
                assert_true(isinstance(path, Path))
                assert_equal(f'test-<timestamp>.{ext}',
                             re.sub(r'20\d{6}-\d{6}', '<timestamp>', path.name))

    def test_result_files_as_none(self):
        for name in 'Output', 'Report', 'Log', 'XUnit', 'DebugFile':
            attr = (name[:-4] if name.endswith('File') else name).lower()
            for value in 'None', 'NONE', None:
                for timestamp_outputs in True, False:
                    settings = RobotSettings({name.lower(): value,
                                              'timestampoutputs': timestamp_outputs})
                    assert_equal(settings[name], None)
                    if hasattr(settings, attr):
                        assert_equal(getattr(settings, attr), None)

    def test_output_dir(self):
        for value in '.', Path('.'), Path('.').absolute():
            assert_equal(RobotSettings({'outputdir': value}).output_directory,
                         Path('.').absolute())

    def test_rerun_failed_as_none_string_and_object(self):
        for name in 'ReRunFailed', 'ReRunFailedSuites':
            assert_equal(RobotSettings({name.lower(): 'NONE'})[name], None)
            assert_equal(RobotSettings({name.lower(): 'NoNe'})[name], None)
            assert_equal(RobotSettings({name.lower(): None})[name], None)

    def test_rerun_failed_as_pathlib_object(self):
        for name in 'ReRunFailed', 'ReRunFailedSuites':
            assert_equal(RobotSettings({name.lower(): Path('R.xml')})[name], 'R.xml')

    def test_doc(self):
        assert_equal(RobotSettings()['Doc'], None)
        assert_equal(RobotSettings({'doc': None})['Doc'], None)
        assert_equal(RobotSettings({'doc': 'The doc!'})['Doc'], 'The doc!')

    def test_doc_from_file(self):
        for doc in __file__, Path(__file__):
            doc = RobotSettings({'doc': doc})['Doc']
            assert_true('def test_doc_from_file(self):' in doc)

    def test_log_levels(self):
        self._verify_log_level('TRACE')
        self._verify_log_level('DEBUG')
        self._verify_log_level('INFO')
        self._verify_log_level('WARN')
        self._verify_log_level('NONE')

    def test_default_log_level(self):
        self._verify_log_levels(RobotSettings(), 'INFO')
        self._verify_log_levels(RebotSettings(), 'TRACE')

    def test_pythonpath(self):
        curdir = normpath(dirname(abspath(__file__)))
        for inp, exp in [('foo', [abspath('foo')]),
                         (['a:b:c', 'zap'], [abspath(p) for p in ('a', 'b', 'c', 'zap')]),
                         (['foo;bar', 'zap'], [abspath(p) for p in ('foo', 'bar', 'zap')]),
                         (join(curdir, 't*_set*.??'), [join(curdir, 'test_settings.py')])]:
            assert_equal(RobotSettings(pythonpath=inp).pythonpath, exp)
        if WINDOWS:
            assert_equal(RobotSettings(pythonpath=r'c:\temp:d:\e\f:g').pythonpath,
                         [r'c:\temp', r'd:\e\f', abspath('g')])
            assert_equal(RobotSettings(pythonpath=r'c:\temp;d:\e\f;g').pythonpath,
                         [r'c:\temp', r'd:\e\f', abspath('g')])

    def test_get_rebot_settings_returns_only_rebot_settings(self):
        expected = RebotSettings()
        for opt in RobotSettings().get_rebot_settings()._opts:
            assert_true(opt in expected, opt)

    def test_get_rebot_settings_excludes_settings_handled_already_in_execution(self):
        settings = RobotSettings(
            name='N', doc=':doc:', metadata='m:d', settag='s',
            include='i', exclude='e', test='t', suite='s',
            output='out.xml', loglevel='DEBUG:INFO', timestampoutputs=True
        ).get_rebot_settings()
        for name in 'Name', 'Doc', 'Output':
            assert_equal(settings[name], None)
        for name in 'Metadata', 'SetTag', 'Include', 'Exclude', 'TestNames', 'SuiteNames':
            assert_equal(settings[name], [])
        assert_equal(settings['LogLevel'], 'TRACE')
        assert_equal(settings['TimestampOutputs'], False)

    def _verify_log_level(self, input, level=None, default=None):
        level = level or input
        default = default or level
        self._verify_log_levels(RobotSettings({'loglevel': input}), level, default)
        self._verify_log_levels(RebotSettings({'loglevel': input}), level, default)

    def _verify_log_levels(self, settings, level, default=None):
        assert_equal(settings['LogLevel'], level)
        assert_equal(settings['VisibleLogLevel'], default or level)

    def test_log_levels_with_default(self):
        self._verify_log_level('TRACE:INFO', level='TRACE', default='INFO')
        self._verify_log_level('TRACE:debug', level='TRACE', default='DEBUG')
        self._verify_log_level('DEBUG:INFO', level='DEBUG', default='INFO')

    def test_invalid_log_level(self):
        self._verify_invalid_log_level('kekonen')
        self._verify_invalid_log_level('DEBUG:INFO:FOO')
        self._verify_invalid_log_level('INFO:bar')
        self._verify_invalid_log_level('bar:INFO')

    def test_visible_level_higher_than_normal_level(self):
        self._verify_invalid_log_level('INFO:TRACE')
        self._verify_invalid_log_level('DEBUG:TRACE')

    def _verify_invalid_log_level(self, input):
        self.assertRaises(DataError, RobotSettings, {'loglevel': input})


if __name__ == '__main__':
    unittest.main()
