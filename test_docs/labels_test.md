---
tags: theme_dark, status_draft, priority_high
categories:
  - type_documentation
  - version_1.0
labels: category_test_suite
---

# Labels Test Note

This note tests the label parsing with underscores.

## Expected Labels

The frontmatter should create the following labels in Trilium:

- `#theme=dark`
- `#status=draft`
- `#priority=high`
- `#type=documentation`
- `#version=1.0`
- `#category=test_suite`

All notes should also have `#readOnly` label automatically added.
