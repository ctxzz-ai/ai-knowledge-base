#!/usr/bin/env python3
import argparse
import os
import datetime
import re

DATA_DIR = "data"

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
    if not os.path.exists(args.content_file):
        return

    with open(args.content_file, 'r', encoding='utf-8') as f:
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
