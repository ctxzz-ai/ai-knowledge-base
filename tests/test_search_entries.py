import unittest
import os
import sys
from io import StringIO
from scripts.search_entries import parse_markdown_file

class TestSearchEntries(unittest.TestCase):
    def test_parse_markdown_file_invalid_yaml(self):
        content = "---\n[invalid yaml\n---\nbody"
        filepath = "test.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Capture stderr
        old_stderr = sys.stderr
        sys.stderr = StringIO()

        try:
            metadata, body = parse_markdown_file(filepath)

            # Assertions
            self.assertIsNone(metadata)
            self.assertEqual(body, content) # Note: the function returns None, content if YAML fails
            self.assertIn("Error parsing YAML in test.md", sys.stderr.getvalue())
        finally:
            sys.stderr = old_stderr
            os.remove(filepath)

if __name__ == '__main__':
    unittest.main()
