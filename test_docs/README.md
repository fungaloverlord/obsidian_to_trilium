# Test Suite Documentation

This directory contains test files to validate all features of the Markdown to Trilium converter.

## Test Files

### 1. `basic_test.md`
Tests basic Markdown formatting:
- Headers
- Bold, italic, code
- Lists (ordered and unordered)
- Code blocks

### 2. `labels_test.md`
Tests YAML frontmatter label parsing:
- Underscore-separated labels (e.g., `theme_dark` → `#theme=dark`)
- Multiple label sources (tags, categories, labels)
- Different formats (comma-separated, YAML lists)

### 2b. `hierarchical_labels_test.md`
Tests hierarchical label parsing:
- Slash-separated labels (e.g., `period/ancient-greek` → `#period=ancient-greek`)
- Underscore-separated labels (e.g., `category_ethics` → `#category=ethics`)
- Multiple values for same label name (e.g., `theme/justice` and `theme/polis`)
- Plain labels without separators

### 3. `wiki_links_test.md`
Tests wiki-style links:
- Simple links: `[[note_name]]`
- Links with display text: `[[note_name|Display]]`
- Path-based links: `[[parent/note_name|Display]]`
- Non-existent note links (should create placeholders)

### 4. `callouts_test.md`
Tests all Obsidian-style callout types:
- note, tip, important, warning, caution
- info, success, question, danger, bug
- example, quote
- Callouts with custom titles
- Callouts with code blocks and lists

### 5. `combined_features.md`
Tests feature combinations:
- Wiki links inside callouts
- Callouts with code and links
- Tables with wiki links
- Task lists
- Nested formatting

### 6. `subfolder/`
Tests directory hierarchy:
- Nested notes in subdirectories
- Cross-directory wiki links
- Folder note creation

## Expected Results in Trilium

### Labels
All notes should have:
- `#readOnly` label (automatically added)
- Labels from frontmatter with proper name-value pairs

### Hierarchy
```
test_docs (folder note)
├── basic_test
├── labels_test
├── wiki_links_test
├── callouts_test
├── combined_features
├── README
└── subfolder (folder note)
    ├── nested_note
    └── another_nested
```

### Wiki Links
- All `[[note_name]]` links should resolve to proper Trilium reference links
- Non-existent notes should create placeholder notes under the trash folder
- Path-based links should extract correct note names

### Callouts
- All callout types should render with proper colors and icons
- Wiki links inside callouts should work correctly
- Code blocks and other formatting should be preserved

## Running the Test

```bash
source .venv/bin/activate
python md_to_trilium.py test_docs --token YOUR_TOKEN
```

Or use the run script:
```bash
./run.bat
```
