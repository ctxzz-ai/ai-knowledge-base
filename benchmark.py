import timeit
import re
import yaml
import os

# Create dummy markdown file
with open('dummy.md', 'w') as f:
    f.write("---\ntitle: test\ntags: [a, b]\n---\nHello world\n")

def parse_markdown_file_original():
    with open('dummy.md', 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)

FRONTMATTER_REGEX = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)

def parse_markdown_file_optimized():
    with open('dummy.md', 'r', encoding='utf-8') as f:
        content = f.read()
    match = FRONTMATTER_REGEX.match(content)

original_time = timeit.timeit("parse_markdown_file_original()", globals=globals(), number=10000)
optimized_time = timeit.timeit("parse_markdown_file_optimized()", globals=globals(), number=10000)

print(f"Original: {original_time:.4f}s")
print(f"Optimized: {optimized_time:.4f}s")

os.remove('dummy.md')
