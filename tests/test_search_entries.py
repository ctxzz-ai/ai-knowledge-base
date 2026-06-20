import unittest
import os
import sys
import tempfile
import shutil
from io import StringIO
from unittest.mock import patch
from scripts.search_entries import parse_markdown_file, search_entries

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

    def test_search_entries_invalid_yaml(self):
        temp_dir = tempfile.mkdtemp()

        valid_content = "---\ntitle: Valid\ntags:\n  - test\n---\nbody"
        invalid_content = "---\n[invalid yaml\n---\nbody"

        valid_filepath = os.path.join(temp_dir, "valid.md")
        invalid_filepath = os.path.join(temp_dir, "invalid.md")

        with open(valid_filepath, 'w', encoding='utf-8') as f:
            f.write(valid_content)
        with open(invalid_filepath, 'w', encoding='utf-8') as f:
            f.write(invalid_content)

        with patch('scripts.search_entries.DATA_DIR', temp_dir):
            old_stderr = sys.stderr
            sys.stderr = StringIO()
            try:
                results = search_entries()
                stderr_output = sys.stderr.getvalue()
            finally:
                sys.stderr = old_stderr

        shutil.rmtree(temp_dir)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Valid')
        self.assertIn("Error parsing YAML in", stderr_output)

if __name__ == '__main__':
    unittest.main()
