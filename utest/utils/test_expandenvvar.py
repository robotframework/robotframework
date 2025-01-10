import unittest
import os
from unittest.mock import patch
from src.robot.utils.argumentparser import EnvironmentVariableExpander
import os
import sys
import io
import tempfile
from robot import run_cli

class TestEnvironmentVariableExpander(unittest.TestCase):
    #--------------------------------
    #linux or macos style expansion tests using $VAR or ${VAR})
    #--------------------------------
    @patch('os.name', 'posix')
    @patch.dict(os.environ, {'HOME': '/fake/home', 'USER': 'fakeuser'}, clear=True)
    def test_posix_expansion_basic(self):
        #$VAR or ${VAR} should be expanded
        expander = EnvironmentVariableExpander(ignore_case=False)
        self.assertEqual(
            expander.resolve_env_variable('My home is $HOME'),
            'My home is /fake/home'
        )
        self.assertEqual(
            expander.resolve_env_variable('User is ${USER}'),
            'User is fakeuser'
        )

    @patch('os.name', 'posix')
    @patch.dict(os.environ, {'HOME': '/fake/home'}, clear=True)
    def test_posix_missing_variable(self):
        #missing variables should remain as $VAR
        expander = EnvironmentVariableExpander(ignore_case=False)
        self.assertEqual(
            expander.resolve_env_variable('User = $USER'),
            'User = $USER'
        )

    @patch('os.name', 'posix')
    @patch.dict(os.environ, {'DOLLAR': 'SHOULD_NOT_SEE_ME'}, clear=True)
    def test_posix_escaping_dollar_sign(self):
        expander = EnvironmentVariableExpander(ignore_case=False)
        # '$$HOME' should become '$HOME' (not expended)
        self.assertEqual(
            expander.resolve_env_variable('$$HOME'),
            '$HOME'
        )

    @patch('os.name', 'posix')
    @patch.dict(os.environ, {'MYVAR': 'myvalue'}, clear=True)
    def test_posix_expand_arguments(self):
        #test with a dict of options and a list of arguments
        expander = EnvironmentVariableExpander(ignore_case=False)
        options = {
            '--option1': 'Value is $MYVAR',
            '--option2': [1, 2, '$MYVAR'],
            '--option3': True  
        }
        arguments = ['somepositional', '$MYVAR']

        expanded_options, expanded_arguments = expander.expand_arguments(options, arguments)

        self.assertEqual(expanded_options['--option1'], 'Value is myvalue')
        self.assertEqual(expanded_options['--option2'], [1, 2, 'myvalue'])
        self.assertTrue(expanded_options['--option3']) 
        self.assertEqual(expanded_arguments, ['somepositional', 'myvalue'])

    #--------------------------------
    #windows expansion tests (using %VAR%)
    #--------------------------------
    @patch('os.name', 'nt')
    @patch.dict(os.environ, {'USERNAME': 'fakeuser'}, clear=True)
    def test_windows_expansion_basic(self):
        #%VAR% should be converted to $VAR
        expander = EnvironmentVariableExpander(ignore_case=True)
        self.assertEqual(
            expander.resolve_env_variable('User = %USERNAME%'),
            'User = fakeuser'
        )

    @patch('os.name', 'nt')
    @patch.dict(os.environ, {}, clear=True)
    def test_windows_missing_variable(self):
        #not found -> remains $USERPROFILE
        expander = EnvironmentVariableExpander(ignore_case=True)
        self.assertEqual(
            expander.resolve_env_variable('Path = %USERPROFILE%'),
            'Path = $USERPROFILE'
        )

    @patch('os.name', 'nt')
    @patch.dict(os.environ, {'DOLLAR': 'SHOULD_NOT_SEE_ME'}, clear=True)
    def test_windows_escaping_dollar_sign(self):
        expander = EnvironmentVariableExpander(ignore_case=True)
        # $$ becomes a single $ in final output
        self.assertEqual(
            expander.resolve_env_variable('$$HOME'),
            '$HOME'
        )

    @patch('os.name', 'nt')
    @patch.dict(os.environ, {'VAR1': 'val1', 'VAR2': 'val2'}, clear=True)
    def test_windows_expand_arguments(self):
        #testing expansion in option values and positional arguments
        expander = EnvironmentVariableExpander(ignore_case=True)
        options = {
            '--foo': '%VAR1%',
            '--bar': [123, '%VAR2%', '%VAR1%'],
            '--baz': False
        }
        arguments = ['positional', '%VAR2%']

        expanded_options, expanded_arguments = expander.expand_arguments(options, arguments)

        self.assertEqual(expanded_options['--foo'], 'val1')
        self.assertEqual(expanded_options['--bar'], [123, 'val2', 'val1'])
        self.assertFalse(expanded_options['--baz']) 
        self.assertEqual(expanded_arguments, ['positional', 'val2'])

    # -------------------------
    # testing case sensitivity
    # -------------------------
    @patch('os.name', 'posix')
    @patch.dict(os.environ, {'MyVar': 'posixval'}, clear=True)
    def test_posix_case_sensitive(self):
        # $MyVar works but $MYVAR no
        expander = EnvironmentVariableExpander(ignore_case=False)
        self.assertEqual(expander.resolve_env_variable('Value=$MyVar'), 'Value=posixval')
        self.assertEqual(expander.resolve_env_variable('Value=$MYVAR'), 'Value=$MYVAR')

    @patch('os.name', 'nt')
    @patch.dict(os.environ, {'MyVar': 'winval'}, clear=True)
    def test_windows_case_insensitive(self):
        #%MYVAR% or %myvar% or %MyVar% should expand to same value
        expander = EnvironmentVariableExpander(ignore_case=True)
        self.assertEqual(expander.resolve_env_variable('Value=%MyVar%'), 'Value=winval')
        self.assertEqual(expander.resolve_env_variable('Value=%MYVAR%'), 'Value=winval')
        self.assertEqual(expander.resolve_env_variable('Value=%myvar%'), 'Value=winval')




class TestArgumentFileEnvExpansion(unittest.TestCase):

    def setUp(self):
        with open("test_env_in_argfile.robot", "w") as f:
            f.write("""\
*** Settings ***
Library    OperatingSystem

*** Test Cases ***
SimpleTest
    Log    Just a simple test to ensure we pass.
""")

    def tearDown(self):
        if os.path.exists("test_env_in_argfile.robot"):
            os.remove("test_env_in_argfile.robot")
        if os.path.exists("myargs.txt"):
            os.remove("myargs.txt")

    def _run_cli_and_capture(self, cli_args):
        saved_stdout = sys.stdout
        saved_stderr = sys.stderr
        try:
            out_buffer = io.StringIO()
            err_buffer = io.StringIO()
            sys.stdout = out_buffer
            sys.stderr = err_buffer

            rc = run_cli(cli_args, exit=False)

            self.assertEqual(rc, 0, f"Robot returned a non-zero RC: {rc}")

            return out_buffer.getvalue() + "\n" + err_buffer.getvalue()
        finally:
            sys.stdout = saved_stdout
            sys.stderr = saved_stderr

    def _run_with_argumentfile(self, argfile_content):
        # writes the given string to myargs.txt then calls run_cli with --argumentfile myargs.txt
        with open("myargs.txt", "w") as f:
            f.write(argfile_content)

        return self._run_cli_and_capture(["--argumentfile", "myargs.txt"])

    @patch.dict(os.environ, clear=True)
    def test_basic_expansion_in_argumentfile(self):
        with tempfile.TemporaryDirectory() as tmpdir:

            logs_dir = os.path.join(tmpdir, "robot_logs")
            os.makedirs(logs_dir, exist_ok=True)
            os.environ["MY_OUTPUT_DIR"] = logs_dir

            argfile_content = f"""\
--loglevel 
DEBUG 
--output 
$MY_OUTPUT_DIR/output.xml
--report 
$MY_OUTPUT_DIR/report.html
--log 
$MY_OUTPUT_DIR/log.html
test_env_in_argfile.robot
"""
            output_text = self._run_with_argumentfile(argfile_content)
            self.assertIn(logs_dir, output_text, "Expected expansions in logs or output.")

    @patch.dict(os.environ, clear=True)
    def test_expansion_in_options_and_argumentfile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = os.path.join(tmpdir, "robot_logs")
            os.makedirs(logs_dir, exist_ok=True)
            os.environ["MY_OUTPUT_DIR"] = logs_dir

            argfile_content = """\
--report
$MY_OUTPUT_DIR/report.html
test_env_in_argfile.robot
"""
            with open("myargs.txt", "w") as f:
                f.write(argfile_content)

            cli_args = [
            "--loglevel", "DEBUG",
            "--log", "$MY_OUTPUT_DIR/log.html",
            "--argumentfile", "myargs.txt",
            "test_env_in_argfile.robot"
            ]

            output_text = self._run_cli_and_capture(cli_args)
            # check expansions: robot_logs/report.html and robot_logs/log.html
            self.assertIn(f"{logs_dir}/report.html", output_text)
            self.assertIn(f"{logs_dir}/log.html", output_text)

    @patch.dict(os.environ, clear=True)
    def test_missing_variable_in_argumentfile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            found_path = os.path.join(tmpdir, "robot_logs")
            os.makedirs(found_path, exist_ok=True)
            os.environ["FOUND_VAR"] = found_path
            #  MISSING_VAR is not defined

            argfile_content = """\
--loglevel
DEBUG
--output
$FOUND_VAR/output.xml
--report
$MISSING_VAR/report.html
test_env_in_argfile.robot
"""
            output_text = self._run_with_argumentfile(argfile_content)

            self.assertIn(f"{found_path}/output.xml", output_text)
            # $MISSING_VAR should be explicitly mentioned -> added print in for this case 
            self.assertIn("$MISSING_VAR", output_text)
            self.assertIn("/report.html", output_text)

    @patch.dict(os.environ, clear=True)
    def test_multiple_variables_in_argumentfile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = os.path.join(tmpdir, "robot_logs")
            os.makedirs(logs_dir, exist_ok=True)

            os.environ["VAR1"] = logs_dir
            os.environ["VAR2"] = "MyReport"

            argfile_content = """\
--loglevel
DEBUG
--output
$VAR1/$VAR2-output.xml
--report
$VAR1/${VAR2}-report.html
--log
$VAR1/log.html
test_env_in_argfile.robot
"""
            output_text = self._run_with_argumentfile(argfile_content)

            # $VAR1/$VAR2-output.xml -------> logs_dir/MyReport-output.xml
            self.assertIn(f"{logs_dir}/MyReport-output.xml", output_text)
            self.assertIn(f"{logs_dir}/MyReport-report.html", output_text)
            self.assertIn(f"{logs_dir}/log.html", output_text)

    @unittest.skipUnless(sys.platform.startswith('win'), "test requires Windows for native path logic")
    @patch.dict(os.environ, {'WINDOWS_VAR': 'C:\\RobotLogs'}, clear=True)
    def test_windows_style_variable_in_argumentfile(self):
        argfile_content = """\
--loglevel DEBUG
--output %WINDOWS_VAR%\\output.xml 
--report %WINDOWS_VAR%\\report.html
test_env_in_argfile.robot
"""
        output_text = self._run_with_argumentfile(argfile_content)
        self.assertIn("C:\\RobotLogs\\output.xml", output_text)
        self.assertIn("C:\\RobotLogs\\report.html", output_text)


if __name__ == '__main__':
    unittest.main()
