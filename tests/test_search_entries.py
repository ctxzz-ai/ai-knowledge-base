import unittest
import os
import sys
import tempfile
import shutil
from io import StringIO
from unittest.mock import patch
from scripts.search_entries import parse_markdown_file, search_entries

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

    def test_search_entries_ignore_non_markdown(self):
        temp_dir = tempfile.mkdtemp()

        valid_content = "---\ntitle: Valid MD\ntags:\n  - test\n---\nbody"
        txt_content = "This is a text file, not markdown."
        json_content = '{"title": "JSON file"}'

        valid_filepath = os.path.join(temp_dir, "valid.md")
        txt_filepath = os.path.join(temp_dir, "document.txt")
        json_filepath = os.path.join(temp_dir, "data.json")
        no_ext_filepath = os.path.join(temp_dir, "file_with_no_extension")

        with open(valid_filepath, 'w', encoding='utf-8') as f:
            f.write(valid_content)
        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        with open(json_filepath, 'w', encoding='utf-8') as f:
            f.write(json_content)
        with open(no_ext_filepath, 'w', encoding='utf-8') as f:
            f.write("No extension file")

        with patch('scripts.search_entries.DATA_DIR', temp_dir):
            results = search_entries()

        shutil.rmtree(temp_dir)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Valid MD')
        self.assertTrue(results[0]['filepath'].endswith('valid.md'))

if __name__ == '__main__':
    unittest.main()
