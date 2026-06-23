import os
import subprocess
import tempfile
import unittest
import sys

# Determine paths relative to the test script
TEST_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_ROOT = os.path.dirname(TEST_DIR)
ADD_ENTRY_SCRIPT = os.path.join(REPO_ROOT, "scripts", "add_entry.py")
DATA_DIR = os.path.join(REPO_ROOT, "data")

sys.path.insert(0, REPO_ROOT)
from scripts.add_entry import sanitize_filename

class TestSanitizeFilename(unittest.TestCase):
    def test_normal_string(self):
        self.assertEqual(sanitize_filename("Normal Title"), "normal-title.md")
        self.assertEqual(sanitize_filename("HelloWorld"), "helloworld.md")

    def test_special_characters(self):
        self.assertEqual(sanitize_filename("Title with!@# special $ chars"), "title-with-special-chars.md")
        self.assertEqual(sanitize_filename("Test 123 !@#"), "test-123.md")

    def test_multiple_spaces_and_dashes(self):
        self.assertEqual(sanitize_filename("Title   with --- spaces"), "title-with-spaces.md")

    def test_leading_trailing_special_chars(self):
        self.assertEqual(sanitize_filename("!!!Leading and Trailing???"), "leading-and-trailing.md")
        self.assertEqual(sanitize_filename("-already-dashed-"), "already-dashed.md")

    def test_empty_or_all_special(self):
        self.assertEqual(sanitize_filename(""), ".md")
        self.assertEqual(sanitize_filename("!@#$%^&*()"), ".md")

class TestAddEntryE2E(unittest.TestCase):
    def test_valid_path(self):
        # Create a temporary file inside the repo root for testing
        fd, temp_file_path = tempfile.mkstemp(dir=REPO_ROOT, suffix=".md")
        os.close(fd)

        try:
            with open(temp_file_path, "w") as f:
                f.write("Valid content inside repo")

            # Call the script
            result = subprocess.run([
                "python3", ADD_ENTRY_SCRIPT,
                "--title", "test_valid",
                "--content-file", temp_file_path
            ], capture_output=True, text=True)

            self.assertEqual(result.returncode, 0, f"Expected success but got error: {result.stderr}")

            # Check if the file was created in DATA_DIR
            output_file = os.path.join(DATA_DIR, "test-valid.md")
            self.assertTrue(os.path.exists(output_file), "Expected file was not created in DATA_DIR")

            # Cleanup created file
            if os.path.exists(output_file):
                os.remove(output_file)

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def test_path_traversal_outside_repo(self):
        # Attempt to read a file outside the repository (e.g., /etc/passwd or a temp file outside)
        fd, temp_file_path = tempfile.mkstemp(suffix=".md") # mkstemp defaults to /tmp which is outside REPO_ROOT
        os.close(fd)

        try:
            with open(temp_file_path, "w") as f:
                f.write("Content outside repo")

            # Call the script with path outside repo
            result = subprocess.run([
                "python3", ADD_ENTRY_SCRIPT,
                "--title", "test_invalid",
                "--content-file", temp_file_path
            ], capture_output=True, text=True)

            # Should fail with exit code 1
            self.assertEqual(result.returncode, 1, "Expected failure but script succeeded")
            self.assertIn("outside the repository root", result.stderr)

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    def test_nonexistent_file(self):
        # Pass a path that doesn't exist
        nonexistent_path = os.path.join(REPO_ROOT, "does_not_exist.md")

        result = subprocess.run([
            "python3", ADD_ENTRY_SCRIPT,
            "--title", "test_nonexistent",
            "--content-file", nonexistent_path
        ], capture_output=True, text=True)

        # Should fail with exit code 1
        self.assertEqual(result.returncode, 1, "Expected failure but script succeeded")
        self.assertIn("does not exist", result.stderr)

if __name__ == "__main__":
    unittest.main()
