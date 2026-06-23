import time
import os
import shutil
import tempfile
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
import constants
import search_entries

def create_dummy_data(data_dir, num_files):
    os.makedirs(data_dir, exist_ok=True)
    for i in range(num_files):
        with open(os.path.join(data_dir, f"dummy_{i}.md"), "w") as f:
            f.write("---\n")
            f.write(f"title: Dummy File {i}\n")
            f.write(f"tags: [dummy, test]\n")
            f.write(f"query: Query {i}\n")
            f.write("---\n")
            f.write(f"This is the body of dummy file {i}.\n")
            f.write(f"It has some text that we might search for.\n")
            f.write(f"Keyword might be found here or there.\n")

def run_benchmark():
    temp_dir = tempfile.mkdtemp()
    try:
        # Patch DATA_DIR in search_entries module
        search_entries.DATA_DIR = temp_dir

        print(f"Creating 5000 dummy files in {temp_dir}...")
        create_dummy_data(temp_dir, 5000)

        print("Running search baseline...")
        start = time.time()
        for _ in range(5): # run 5 times
            search_entries.search_entries(keyword="KeYwOrD")
        end = time.time()

        print(f"Total time for 5 searches: {end - start:.4f} seconds")
        print(f"Average time per search: {(end - start)/5:.4f} seconds")

    finally:
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    run_benchmark()
