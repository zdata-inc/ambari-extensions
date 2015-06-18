import unittest
import __builtin__ as builtins #pylint:disable=import-error
from mock.mock import Mock, patch, mock_open

import logging
from resource_management.core.system import System
from resource_management.core.environment import Environment
from resource_management.core.source import StaticFile
from textwrap import dedent

import utilities # pylint:disable=import-error

@patch.object(System, "os_family", new='redhat')
class TestUtilities(unittest.TestCase):
    def setUp(self):
        logging.getLogger('resource_management').setLevel(logging.CRITICAL)

    @patch.object(utilities, 'append_to_file')
    def test_append_to_profile(self, append_to_file_mock):
        utilities.append_bash_profile('testuser', 'testcommand')
        self.assertTrue(append_to_file_mock.called)

    @patch.object(utilities, 'append_to_file')
    @patch("resource_management.core.providers.system.ExecuteProvider")
    def test_append_to_profile_run(self, append_to_file_mock, execute_mock):
        with Environment('/'):
            utilities.append_bash_profile('testuser', 'testcommand', True)
            self.assertTrue(append_to_file_mock.called)
            self.assertTrue(execute_mock.called)

    def test_append_to_file(self):
        open_mock = mock_open()
        with Environment('/'):
            with patch.object(builtins, 'open', open_mock, create=True):
                utilities.append_to_file('/test', 'some_command')

        open_mock.assert_called_once_with('/test', 'a+')
        handle = open_mock()
        handle.write.assert_called_once_with("some_command\n")

    def test_append_to_file_no_duplicates(self):
        bashrc_contents = "# .bashrc file\nsome_command\n"

        open_mock = mock_open()
        open_mock.return_value.readlines = Mock(return_value=bashrc_contents.split("\n"))

        with patch.object(builtins, 'open', open_mock, create=True):
            with Environment('/'):
                utilities.append_to_file('/test', 'some_command')

        self.assertTrue('/test' in open_mock.call_args[0], "Wrong file being edited.")

        handle = open_mock()
        self.assertEqual(handle.write.call_count, 0, "Text appended despite duplicate text existing.")

    @patch.object(StaticFile, 'get_content')
    def test_get_configuration_file(self, static_file_mock):
        with Environment('/'):
            static_file_mock.return_value = dedent("""
                key1=value1
                key2=value2
                #key3=value3
            """)

            testresult = utilities.get_configuration_file('testfile')

        self.assertDictContainsSubset({'key1':'value1', 'key2':'value2'}, testresult)
        self.assertFalse(testresult.has_key('key3'))

    def test_parse_pattern_sequence_parsing(self):
        self.assertEqual(
            utilities.parse_path_pattern_expression('[1-2]', 5),
            ['1', '2', '1', '2', '1']
        )

        self.assertEqual(
            utilities.parse_path_pattern_expression('[1-2]', 6),
            ['1', '2', '1', '2', '1', '2']
        )

        self.assertEqual(
            utilities.parse_path_pattern_expression('/data[1-2]/primary', 3),
            ['/data1/primary', '/data2/primary', '/data1/primary']
        )

if __name__ == '__main__':
    unittest.main()
