#!/usr/bin/env python3
import argparse
import os
import yaml
import re
import json

DATA_DIR = "data"
CACHE_FILE = os.path.join(DATA_DIR, ".search_cache.json")

def parse_markdown_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1)), match.group(2)
        except yaml.YAMLError:
            pass
    return None, content

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}

import datetime

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)

def save_cache(cache):
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, cls=DateTimeEncoder)
    except IOError:
        pass

def search_entries(keyword=None, tag=None):
    results = []
    if not os.path.exists(DATA_DIR): return results

    cache = load_cache()
    cache_modified = False
    current_files = set()

    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".md"): continue
        current_files.add(filename)
        filepath = os.path.join(DATA_DIR, filename)

        try:
            mtime = os.path.getmtime(filepath)
        except OSError:
            continue

        if filename in cache and cache[filename].get("mtime") == mtime:
            metadata = cache[filename].get("metadata")
            body = cache[filename].get("body")
        else:
            metadata, body = parse_markdown_file(filepath)
            cache[filename] = {
                "mtime": mtime,
                "metadata": metadata,
                "body": body
            }
            cache_modified = True

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

    # Remove deleted files from cache
    stale_keys = [k for k in cache.keys() if k not in current_files]
    if stale_keys:
        for k in stale_keys:
            del cache[k]
        cache_modified = True

    if cache_modified:
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
