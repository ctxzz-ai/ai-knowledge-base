#!/usr/bin/env python3
import argparse
import os
import sys
import datetime
import re
import yaml

# Determine repo root dynamically relative to this script
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from constants import REPO_ROOT, DATA_DIR

def sanitize_filename(title):
    filename = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    return filename + ".md"

def create_frontmatter(title, query, tags, date_str):
    metadata = {
        "title": title,
        "date": date_str,
    }
    if query:
        metadata["query"] = query
    if tags:
        metadata["tags"] = tags

    yaml_str = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True)
    return f"---\n{yaml_str}---\n\n"

def main():
    parser = argparse.ArgumentParser(description="Add a new research entry to the knowledge base.")
    parser.add_argument("--title", required=True, help="Title of the research entry.")
    parser.add_argument("--content-file", required=True, help="Path to the Markdown content.")
    parser.add_argument("--query", help="The original question or query.")
    parser.add_argument("--tags", nargs='*', default=[], help="List of tags.")
    args = parser.parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)

    try:
        content_file_path = os.path.realpath(args.content_file)
        if os.path.commonpath([REPO_ROOT, content_file_path]) != REPO_ROOT:
            print(f"Error: content_file '{args.content_file}' is outside the repository root.", file=sys.stderr)
            sys.exit(1)
    except ValueError as e:
        print(f"Error validating content_file path: {e}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(content_file_path):
        print(f"Error: content_file '{args.content_file}' does not exist.", file=sys.stderr)
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
