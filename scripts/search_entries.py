#!/usr/bin/env python3
import argparse
import os
import sys
import yaml
import re
import json
import datetime

DATA_DIR = "data"
CACHE_FILE = os.path.join(DATA_DIR, ".search_cache.json")

def parse_markdown_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1)), match.group(2)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML in {filepath}: {e}", file=sys.stderr)
    return None, content

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def save_cache(cache):
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, default=json_serial)
    except IOError as e:
        print(f"Warning: Could not save cache: {e}", file=sys.stderr)

def search_entries(keyword=None, tag=None):
    results = []
    if not os.path.exists(DATA_DIR): return results

    cache = load_cache()
    cache_updated = False

    # Evict deleted files from cache
    current_files = {f for f in os.listdir(DATA_DIR) if f.endswith(".md")}
    for cached_filename in list(cache.keys()):
        if cached_filename not in current_files:
            del cache[cached_filename]
            cache_updated = True

    for filename in current_files:
        filepath = os.path.join(DATA_DIR, filename)

        try:
            mtime = os.path.getmtime(filepath)
        except OSError:
            continue

        if filename in cache and cache[filename].get('mtime') == mtime:
            metadata = cache[filename]['metadata']
            body = cache[filename]['body']
        else:
            metadata, body = parse_markdown_file(filepath)
            if metadata:
                cache[filename] = {'mtime': mtime, 'metadata': metadata, 'body': body}
                cache_updated = True
            elif filename in cache:
                del cache[filename]
                cache_updated = True

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

    if cache_updated:
        save_cache(cache)

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
