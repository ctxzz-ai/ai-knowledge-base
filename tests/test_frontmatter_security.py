import unittest
import os
import sys
import yaml
import tempfile
import subprocess

# Adjust the path to import scripts.add_entry
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, REPO_ROOT)

from scripts.add_entry import create_frontmatter

class TestAddEntrySecurity(unittest.TestCase):
    def test_yaml_injection_mitigation(self):
        """Test that malicious strings do not cause YAML injection"""
        malicious_title = 'My Title"\nmalicious_key: "malicious_value'
        malicious_query = 'Query"\nother_key: "value'

        frontmatter = create_frontmatter(malicious_title, malicious_query, ['tag1'], '2023-10-27 10:00:00')

        # Verify it starts and ends with ---
        self.assertTrue(frontmatter.startswith("---\n"))

        # Strip the --- and parse the yaml
        yaml_content = frontmatter.strip().strip('-').strip()
        parsed_metadata = yaml.safe_load(yaml_content)

        self.assertEqual(parsed_metadata['title'], malicious_title)
        self.assertEqual(parsed_metadata['query'], malicious_query)
        self.assertNotIn('malicious_key', parsed_metadata)
        self.assertNotIn('other_key', parsed_metadata)

    def test_path_traversal_prevention(self):
        """Test that paths outside the repository are rejected"""
        # Create a temporary file outside the repo
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"Test content")
            tmp_path = tmp_file.name

        try:
            # Run the script as a subprocess and check the return code and stderr
            result = subprocess.run(
                [sys.executable, os.path.join(REPO_ROOT, 'scripts', 'add_entry.py'),
                 '--title', 'Test', '--content-file', tmp_path],
                capture_output=True, text=True
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("outside the repository root", result.stderr)
        finally:
            os.remove(tmp_path)

    def test_file_not_found_handling(self):
        """Test handling of non-existent files"""
        non_existent_path = os.path.join(REPO_ROOT, 'does_not_exist_file.md')

        result = subprocess.run(
            [sys.executable, os.path.join(REPO_ROOT, 'scripts', 'add_entry.py'),
             '--title', 'Test', '--content-file', non_existent_path],
            capture_output=True, text=True
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not exist", result.stderr)

if __name__ == '__main__':
    unittest.main()
