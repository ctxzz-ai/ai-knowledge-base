import os
import subprocess
import tempfile
import shutil

# Determine paths relative to the test script
TEST_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_ROOT = os.path.dirname(TEST_DIR)
ADD_ENTRY_SCRIPT = os.path.join(REPO_ROOT, "scripts", "add_entry.py")
DATA_DIR = os.path.join(REPO_ROOT, "data")

def test_valid_path():
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

        assert result.returncode == 0, f"Expected success but got error: {result.stderr}"

        # Check if the file was created in DATA_DIR
        output_file = os.path.join(DATA_DIR, "test-valid.md")
        assert os.path.exists(output_file), "Expected file was not created in DATA_DIR"

        # Cleanup created file
        if os.path.exists(output_file):
            os.remove(output_file)

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def test_path_traversal_outside_repo():
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
        assert result.returncode == 1, "Expected failure but script succeeded"
        assert "Error: Access denied" in result.stderr, f"Expected 'Access denied' error, but got: {result.stderr}"

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def test_nonexistent_file():
    # Pass a path that doesn't exist
    nonexistent_path = os.path.join(REPO_ROOT, "does_not_exist.md")

    result = subprocess.run([
        "python3", ADD_ENTRY_SCRIPT,
        "--title", "test_nonexistent",
        "--content-file", nonexistent_path
    ], capture_output=True, text=True)

    # Should fail with exit code 1
    assert result.returncode == 1, "Expected failure but script succeeded"
    assert "does not exist" in result.stderr, f"Expected 'does not exist' error, but got: {result.stderr}"

if __name__ == "__main__":
    print("Running tests...")
    test_valid_path()
    print("test_valid_path passed")
    test_path_traversal_outside_repo()
    print("test_path_traversal_outside_repo passed")
    test_nonexistent_file()
    print("test_nonexistent_file passed")
    print("All tests passed!")
