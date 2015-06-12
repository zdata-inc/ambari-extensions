import unittest
import __builtin__ as builtins
from mock.mock import patch, mock_open

from resource_management.core.environment import Environment
from resource_management.core.resources.system import Execute
from resource_management.core.source import StaticFile
from textwrap import dedent

import utilities # pylint:disable=import-error

class TestUtilities(unittest.TestCase):
    @patch.object(utilities, 'append_to_file')
    def test_append_to_profile(self, append_to_file_mock):
        utilities.append_bash_profile('testuser', 'testcommand')
        self.assertTrue(append_to_file_mock.called)

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
