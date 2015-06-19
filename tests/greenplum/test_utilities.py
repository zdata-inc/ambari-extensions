try:
    import unittest2 as unittest
except ImportError:
    import unittest

from unittest_data_provider import data_provider
import __builtin__ as builtins #pylint:disable=import-error
from mock.mock import Mock, patch, mock_open

from textwrap import dedent
import math
import collections

from pprint import pprint, pformat

from contextlib import contextmanager

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

    def __mock_file(self, return_value=""):
        open_mock = mock_open(read_data=return_value)
        open_mock.return_value.readlines = Mock(return_value=return_value.split("\n"))

        return open_mock

    @contextmanager
    def __with_mocked_file(self, mocked_file):
        with patch.object(builtins, 'open', mocked_file, create=True):
            yield

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
        mocked_file = self.__mock_file()

        with self.__with_mocked_file(mocked_file), Environment('/'):
            utilities.append_to_file('/test', 'some_command')

        mocked_file.assert_called_once_with('/test', 'a+')
        handle = mocked_file()
        handle.write.assert_called_once_with("some_command\n")

    def test_append_to_file_no_duplicates(self):
        bashrc_contents = "# .bashrc file\nsome_command\n"
        mocked_file = self.__mock_file(bashrc_contents)

        with self.__with_mocked_file(mocked_file), Environment('/'):
            utilities.append_to_file('/test', 'some_command')

        self.assertTrue('/test' in mocked_file.call_args[0], "Wrong file being edited.")

        handle = mocked_file()
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

    @patch("resource_management.core.providers.system.ExecuteProvider")
    def test_set_kernel_parameter(self, execute_mock):
        sysctl_contents = ""
        mocked_file = self.__mock_file(sysctl_contents)

        with self.__with_mocked_file(mocked_file), Environment('/'):
            utilities.set_kernel_parameter('pname', 'pvalue')

        self.assertTrue(execute_mock.called)

        execute_mock_called_command = execute_mock.call_args[0][0].command
        self.assertTrue(
            'sysctl -w pname="pvalue"' in execute_mock_called_command,
            "Invalid sysctl command called. %s" % pformat(execute_mock_called_command)
        )

        handle = mocked_file()

        handle.write.assert_called_once_with("pname = pvalue\n")

    @patch("resource_management.core.providers.system.ExecuteProvider")
    def test_set_duplicate_kernel_parameter(self, execute_mock):
        sysctl_contents = "#sysctl file\npname = pvalue\n"
        mocked_file = self.__mock_file(sysctl_contents)

        with self.__with_mocked_file(mocked_file), Environment('/'):
            utilities.set_kernel_parameter('pname', 'pvalue')

        self.assertFalse(execute_mock.called)

        handle = mocked_file()

        self.assertEqual(handle.write.call_count, 0, "Text appended despite duplicate text existing.")

    add_blocks_to_file_dataprovider = lambda: (
        ("", "block", "#SS", "#ES", "#SS\nblock\n#ES\n"),
        ("\n", "block", "#SS", "#ES", "#SS\nblock\n#ES\n"),
        ("test", "block", "#SS", "#ES", "test\n#SS\nblock\n#ES\n"),
        ("test\n", "block", "#SS", "#ES", "test\n#SS\nblock\n#ES\n"),
        ("test\n#SS\nold\n#ES\ntest2", "new", "#SS", "#ES", "test\n#SS\nnew\n#ES\ntest2"),
        ("#SS\nold\n#ES\ntest2", "new", "#SS", "#ES", "#SS\nnew\n#ES\ntest2"),
        ("#SS\nold\n#ES\ntest2\n#SS\nold2\n#ES\ntest3", "new", "#SS", "#ES", "#SS\nnew\n#ES\ntest2\n#SS\nold2\n#ES\ntest3"),
    )

    @data_provider(add_blocks_to_file_dataprovider)
    def test_add_block_to_filestream(self, file_contents, data, start_sentinel, end_sentinel, expected_result):
        new_file_contents = []

        mocked_file = self.__mock_file(file_contents)
        mocked_file.return_value.write = Mock(
            side_effect=lambda s: new_file_contents.append(s) #pylint:disable=unnecessary-lambda
        )

        with self.__with_mocked_file(mocked_file), Environment('/'):
            utilities.add_block_to_file('/test', data, None, start_sentinel, end_sentinel)

        new_file_contents = "".join(new_file_contents)

        self.assertEqual(new_file_contents, expected_result)

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

    def test_gpsshify(self):
        with Environment('/'):
            self.assertEqual(
                utilities.gpsshify('command', host='host1'),
                dedent("""
                cat <<EOF | gpssh -h "host1"
                    command
                EOF""")
            )

            self.assertEqual(
                utilities.gpsshify('command', hostfile='hosts'),
                dedent("""
                cat <<EOF | gpssh -f "hosts"
                    command
                EOF""")
            )

            self.assertEqual(
                utilities.gpsshify('command\'"', host='host1'),
                dedent("""
                cat <<EOF | gpssh -h "host1"
                    command'"
                EOF""")
            )

            self.assertEqual(
                utilities.gpsshify('command', host='host1', args='test'),
                dedent("""
                cat <<EOF | gpssh -h "host1" test
                    command
                EOF""")
            )

            with self.assertRaises(ValueError):
                utilities.gpsshify('command', args='test'),

    def test_random_string(self):
        import string

        self.assertEqual(
            len(utilities.random_string(15)),
            15
        )

        self.assertEqual(
            utilities.random_string(5, ['a']),
            'aaaaa'
        )

        # Verify distribution is reasonably random
        letter_frequencies = collections.defaultdict(lambda: 0)

        for _ in range(1, 10000):
            for letter in utilities.random_string(16):
                letter_frequencies[letter] += 1

        standard_deviation = self.__standard_deviation(letter_frequencies.values())

        self.assertLessEqual(standard_deviation, 100, "Standard deviation of letter frequency is too high!  Are you sure it is random?")

    def __standard_deviation(self, values):
        mean = sum(values) / len(values)
        respective_deviations = [math.pow(count - mean, 2) for count in values]

        return math.sqrt(sum(respective_deviations) / len(values))


if __name__ == '__main__':
    unittest.main()
