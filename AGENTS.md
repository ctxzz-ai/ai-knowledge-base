# Instructions for AI Agents

Welcome. This repository is your designated knowledge base for storing and retrieving research findings.

## Core Principles
1. **Structured Data:** All research findings MUST be stored in the `data/` directory.
2. **Format:** Files must be in Markdown (`.md`) format.
3. **Metadata:** Every Markdown file must begin with YAML frontmatter containing relevant metadata (e.g., `date`, `tags`, `query`, `summary`).
4. **Use Tools:** Do not manually create or search files if possible. Use the provided Python scripts in the `scripts/` directory to manage entries.

## Available Tools
### Adding an Entry
```bash
python scripts/add_entry.py --title "Your Title" --query "original query" --tags tag1 tag2 --content-file path/to/content.md
```

### Searching Entries
```bash
python scripts/search_entries.py --keyword "search term"
python scripts/search_entries.py --tag "tag1"
```

## Workflow for New Research Tasks
1. **Search First:** Run `search_entries.py` to see if similar research exists.
2. **Conduct Research:** Gather information.
3. **Draft Findings:** Draft into a temporary Markdown document.
4. **Save Entry:** Use `add_entry.py` to formally save findings into `data/`.
5. **Clean Up:** Delete temporary files.
