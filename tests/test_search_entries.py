import unittest
import os
import sys
import tempfile
from io import StringIO
from scripts.search_entries import parse_markdown_file

class TestSearchEntries(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.test_dir.cleanup()

    def _create_test_file(self, filename, content):
        filepath = os.path.join(self.test_dir.name, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath

    def test_parse_markdown_file_invalid_yaml(self):
        content = "---\n[invalid yaml\n---\nbody"
        filepath = self._create_test_file("invalid.md", content)

        # Capture stderr
        old_stderr = sys.stderr
        sys.stderr = StringIO()

        try:
            metadata, body = parse_markdown_file(filepath)

            # Assertions
            self.assertIsNone(metadata)
            self.assertEqual(body, content) # Note: the function returns None, content if YAML fails
            self.assertIn("Error parsing YAML in", sys.stderr.getvalue())
        finally:
            sys.stderr = old_stderr

    def test_parse_markdown_file_valid_frontmatter(self):
        content = "---\ntitle: Test\ntags: [a, b]\n---\nbody content here"
        filepath = self._create_test_file("valid.md", content)

        metadata, body = parse_markdown_file(filepath)

        self.assertEqual(metadata, {"title": "Test", "tags": ["a", "b"]})
        self.assertEqual(body, "body content here")

    def test_parse_markdown_file_no_frontmatter(self):
        content = "just body content without frontmatter"
        filepath = self._create_test_file("no_frontmatter.md", content)

        metadata, body = parse_markdown_file(filepath)

        self.assertIsNone(metadata)
        self.assertEqual(body, content)

    def test_parse_markdown_file_empty_file(self):
        content = ""
        filepath = self._create_test_file("empty.md", content)

        metadata, body = parse_markdown_file(filepath)

        self.assertIsNone(metadata)
        self.assertEqual(body, content)

if __name__ == '__main__':
    unittest.main()
