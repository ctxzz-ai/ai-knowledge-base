#!/usr/bin/env python3
import argparse
import os
import sys
import yaml
import re

# Add the directory containing this script to sys.path so we can import constants
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from constants import DATA_DIR

FRONTMATTER_REGEX = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)

def parse_markdown_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    match = FRONTMATTER_REGEX.match(content)
    if match:
        try:
            return yaml.safe_load(match.group(1)), match.group(2)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML in {filepath}: {e}", file=sys.stderr)
    return None, content

def search_entries(keyword=None, tag=None):
    results = []
    if not os.path.exists(DATA_DIR): return results
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".md"): continue
        filepath = os.path.join(DATA_DIR, filename)
        metadata, body = parse_markdown_file(filepath)
        if not metadata: continue

        match = False
        if tag and tag in metadata.get('tags', []):
            match = True
        elif keyword:
            kw = keyword.lower()
            if kw in metadata.get('title', '').lower() or kw in metadata.get('query', '').lower() or kw in body.lower():
                match = True
        else:
            match = True

        if match:
            results.append({'filepath': filepath, 'title': metadata.get('title', 'Untitled'), 'date': metadata.get('date', ''), 'tags': metadata.get('tags', [])})
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", "-k")
    parser.add_argument("--tag", "-t")
    args = parser.parse_args()

    results = search_entries(keyword=args.keyword, tag=args.tag)
    if not results:
        print("No matching entries found.")
        return
    for res in results:
        print(f"- Title: {res['title']}\n  File: {res['filepath']}\n  Date: {res['date']}\n  Tags: {res['tags']}")

if __name__ == "__main__":
    main()
