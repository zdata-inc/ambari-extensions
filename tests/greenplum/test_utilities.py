import unittest

import utilities

class TestUtilities(unittest.TestCase):
    def test_parse_pattern_sequence_parsing(self):
        self.assertEqual(utilities.parse_path_pattern_expression('[1..2]', 5), [1, 2, 1, 2, 1])
        self.assertEqual(utilities.parse_path_pattern_expression('[1..2]', 6), [1, 2, 1, 2, 1, 2])

if __name__ == '__main__':
    unittest.main()
