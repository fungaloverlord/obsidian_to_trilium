---
tags:
  - philosophy
  - period/ancient-greek
  - philosopher/aristotle
  - theme/justice
  - theme/polis
  - category_ethics
---

# Hierarchical Labels Test

This note tests hierarchical label parsing with both "/" and "_" separators.

## Expected Labels

The frontmatter should create the following Trilium labels:

- `#philosophy` (no value)
- `#period=ancient-greek`
- `#philosopher=aristotle`
- `#theme=justice`
- `#theme=polis`
- `#category=ethics`

## Label Format Examples

### Slash Separator (/)
- `period/ancient-greek` → `#period=ancient-greek`
- `philosopher/aristotle` → `#philosopher=aristotle`
- `theme/justice` → `#theme=justice`

### Underscore Separator (_)
- `category_ethics` → `#category=ethics`

### No Separator
- `philosophy` → `#philosophy` (label with no value)

## Content

This is test content to verify that labels are properly extracted from the YAML frontmatter and converted to Trilium label attributes with the correct name-value pairs.

> [!note]
> Labels with "/" or "_" should be split into name=value pairs.

> [!tip]
> Multiple tags can share the same label name with different values (e.g., `theme=justice` and `theme=polis`).
