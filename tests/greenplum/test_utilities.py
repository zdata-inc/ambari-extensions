import unittest

import utilities

class TestUtilities(unittest.TestCase):
    def test_parse_pattern_sequence_parsing(self):
        self.assertEqual(utilities.parse_path_pattern_expression('[1..2]', 5), ['1', '2', '1', '2', '1'])
        self.assertEqual(utilities.parse_path_pattern_expression('[1..2]', 6), ['1', '2', '1', '2', '1', '2'])

        self.assertEqual(utilities.parse_path_pattern_expression('/data[1..2]/primary', 3), ['/data1/primary', '/data2/primary', '/data1/primary'])

if __name__ == '__main__':
    unittest.main()
