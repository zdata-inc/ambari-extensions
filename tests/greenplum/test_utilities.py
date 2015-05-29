import unittest
from resource_management.core.environment import Environment
from mock.mock import patch, MagicMock, call
from resource_management.core.resources.system import Execute

import utilities

class TestUtilities(unittest.TestCase):
    @patch.object(utilities, 'append_to_file')
    def test_append_to_profile(self, append_to_file_mock):
        utilities.append_bash_profile('testuser', 'testcommand')
        self.assertTrue(append_to_file_mock.called)

    def test_parse_pattern_sequence_parsing(self):
        self.assertEqual(
            utilities.parse_path_pattern_expression('[1..2]', 5),
            ['1', '2', '1', '2', '1']
        )

        self.assertEqual(
            utilities.parse_path_pattern_expression('[1..2]', 6),
            ['1', '2', '1', '2', '1', '2']
        )

        self.assertEqual(
            utilities.parse_path_pattern_expression('/data[1..2]/primary', 3),
            ['/data1/primary', '/data2/primary', '/data1/primary']
        )

if __name__ == '__main__':
    unittest.main()
