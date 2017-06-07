import unittest

from robot.conf.settings import _BaseSettings, RobotSettings, RebotSettings
from robot.errors import DataError
from robot.utils.asserts import assert_equal


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

    def test_output_files_as_none_string(self):
        for name in 'Output', 'Report', 'Log', 'XUnit', 'DebugFile':
            attr = (name[:-4] if name.endswith('File') else name).lower()
            settings = RobotSettings({name.lower(): 'NoNe'})
            assert_equal(settings[name], None)
            if hasattr(settings, attr):
                assert_equal(getattr(settings, attr), None)

    def test_output_files_as_none_object(self):
        for name in 'Output', 'Report', 'Log', 'XUnit', 'DebugFile':
            attr = (name[:-4] if name.endswith('File') else name).lower()
            settings = RobotSettings({name.lower(): None})
            assert_equal(settings[name], None)
            if hasattr(settings, attr):
                assert_equal(getattr(settings, attr), None)

    def test_log_levels(self):
        self._verify_log_level('TRACE')
        self._verify_log_level('DEBUG')
        self._verify_log_level('INFO')
        self._verify_log_level('WARN')
        self._verify_log_level('NONE')

    def test_default_log_level(self):
        self._verify_log_levels(RobotSettings(), 'INFO')
        self._verify_log_levels(RebotSettings(), 'TRACE')

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
