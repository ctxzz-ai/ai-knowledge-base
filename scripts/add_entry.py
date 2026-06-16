#!/usr/bin/env python3
import argparse
import os
import sys
import datetime
import re

# Determine the repository root based on the script's location
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(REPO_ROOT, "data")

def sanitize_filename(title):
    filename = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    return filename + ".md"

def create_frontmatter(title, query, tags, date_str):
    frontmatter = "---\n"
    frontmatter += f"title: \"{title}\"\n"
    frontmatter += f"date: {date_str}\n"
    if query:
        frontmatter += f"query: \"{query}\"\n"
    if tags:
        tags_list = "\n".join([f"  - {tag}" for tag in tags])
        frontmatter += f"tags:\n{tags_list}\n"
    frontmatter += "---\n\n"
    return frontmatter

def main():
    parser = argparse.ArgumentParser(description="Add a new research entry to the knowledge base.")
    parser.add_argument("--title", required=True, help="Title of the research entry.")
    parser.add_argument("--content-file", required=True, help="Path to the Markdown content.")
    parser.add_argument("--query", help="The original question or query.")
    parser.add_argument("--tags", nargs='*', default=[], help="List of tags.")
    args = parser.parse_args()

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # Security Fix: Prevent Path Traversal
    content_file_path = os.path.realpath(args.content_file)

    # Check if the resolved path is within the repository root
    if os.path.commonpath([REPO_ROOT, content_file_path]) != REPO_ROOT:
        print(f"Error: Access denied. Path '{args.content_file}' is outside the allowed directory.", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(content_file_path):
        print(f"Error: Content file '{args.content_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(content_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    filename = sanitize_filename(args.title)
    filepath = os.path.join(DATA_DIR, filename)

    if os.path.exists(filepath):
        base, ext = os.path.splitext(filename)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{base}-{timestamp}{ext}"
        filepath = os.path.join(DATA_DIR, filename)

    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    frontmatter = create_frontmatter(args.title, args.query, args.tags, date_str)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter + content)

if __name__ == "__main__":
    main()
