# Markdown to Trilium Converter

A Python application that converts Markdown files to [Trilium Notes](https://github.com/zadam/trilium), preserving directory hierarchy, wiki-style links, YAML frontmatter labels, and Obsidian-style callouts.

## Features

### 🗂️ **Directory Hierarchy Preservation**
- Maintains folder structure as parent/child note relationships
- Folders become parent notes in Trilium
- Markdown files become child notes under their folder's note

### 🔗 **Wiki-Style Links**
- Full support for `[[note_name]]` syntax
- Custom display text: `[[note_name|Display Text]]`
- Path-based links: `[[parent/note_name|Display]]`
- Automatic placeholder creation for missing notes
- Links converted to Trilium reference links

### 🏷️ **YAML Frontmatter Labels**
- Extract labels from frontmatter metadata
- Support for hierarchical tags with `/` or `_` separators
- Multiple label sources: `tags`, `labels`, `categories`

**Examples:**
```yaml
---
tags:
  - philosophy
  - period/ancient-greek    # → #period=ancient-greek
  - philosopher/aristotle   # → #philosopher=aristotle
  - theme/justice           # → #theme=justice
  - category_ethics         # → #category=ethics
---
```

### 📦 **Obsidian-Style Callouts**
- Full support for all Obsidian callout types (27+ variations)
- Beautiful styling with emoji icons and color-coded backgrounds
- Wiki links work inside callouts
- Support for custom titles and nested formatting

**Supported callout types:**
- `note`, `abstract`, `summary`, `tldr`
- `info`, `todo`
- `tip`, `hint`, `important`
- `success`, `check`, `done`
- `question`, `help`, `faq`
- `warning`, `caution`, `attention`
- `failure`, `fail`, `missing`
- `danger`, `error`
- `bug`, `example`, `quote`, `cite`

**Example:**
```markdown
> [!note] Custom Title
> This is a note callout with custom styling and emoji icons.

> [!warning]
> Important warning message!
```

### 🎨 **Rich Markdown Support**
- Fenced code blocks with syntax highlighting
- Tables
- Task lists
- Strikethrough
- Footnotes
- And more via markdown2

## Installation

### Prerequisites
- Python 3.8 or higher
- Trilium Notes server running locally or remotely
- Trilium ETAPI token

### Setup

1. **Clone or download this repository**

2. **Create a virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
# or
pip install -e .
```

4. **Configure environment variables:**
```bash
# Copy the example files
cp .env.example .env
cp .env.test.example .env.test

# Edit .env with your settings
nano .env
```

**.env configuration:**
```bash
TRILIUM_TOKEN=your_trilium_api_token_here
TRILIUM_SERVER=http://localhost:8080
TRILIUM_PARENT_NOTE=root
SOURCE_DIR=/path/to/your/markdown/files
```

### Getting a Trilium ETAPI Token

1. Open Trilium Notes
2. Go to **Options** → **ETAPI**
3. Create a new token
4. Copy the token to your `.env` file

## Usage

### Basic Usage

**Using the run script (recommended):**
```bash
./run.sh
```

**Direct Python command:**
```bash
source .venv/bin/activate
python md_to_trilium.py --token YOUR_TOKEN /path/to/markdown
```

### Command-Line Options

```bash
python md_to_trilium.py [OPTIONS] DIRECTORY

Arguments:
  DIRECTORY             Directory containing Markdown files

Options:
  --token TOKEN         Trilium ETAPI token (required)
  --server URL          Trilium server URL (default: http://localhost:8080)
  --parent NOTEID       Parent note ID in Trilium (default: root)
  --preview             Preview conversion without uploading
```

### Examples

**Convert and upload to Trilium:**
```bash
python md_to_trilium.py --token YOUR_TOKEN /path/to/notes
```

**Preview without uploading:**
```bash
python md_to_trilium.py --token YOUR_TOKEN --preview /path/to/notes
```

**Specify parent note and server:**
```bash
python md_to_trilium.py \
  --token YOUR_TOKEN \
  --server http://localhost:8080 \
  --parent abc123 \
  /path/to/notes
```

## Testing

The project includes a comprehensive test suite in the `test_docs/` directory.

**Run tests:**
```bash
./run_test.sh
```

**Test files include:**
- Basic Markdown formatting
- Hierarchical labels with `/` and `_` separators
- Wiki links (simple, with display text, with paths)
- All 27 callout type variations
- Combined features (callouts + wiki links + labels)
- Directory hierarchy testing

## Project Structure

```
.
├── md_to_trilium.py       # Main CLI application
├── md_converter.py        # Markdown to HTML converter
├── directory_scanner.py   # Directory tree scanner
├── trilium_uploader.py    # Trilium API integration
├── upload_css.py          # CSS uploader script
├── .css                   # Callout styling (Trilium CSS code note)
├── run.sh                 # Production run script
├── run_test.sh            # Test run script
├── upload_css.sh          # Upload CSS to Trilium
├── .env                   # Configuration (not committed)
├── .env.example           # Configuration template
├── .env.test              # Test configuration (not committed)
├── .env.test.example      # Test configuration template
├── test_docs/             # Test suite
│   ├── basic_test.md
│   ├── hierarchical_labels_test.md
│   ├── wiki_links_test.md
│   ├── callouts_test.md
│   └── ...
├── pyproject.toml         # Python project configuration
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## How It Works

### 1. **Scanning**
The `directory_scanner.py` recursively scans your Markdown directory and builds a tree structure representing the hierarchy.

### 2. **Conversion**
The `md_converter.py` converts each Markdown file to HTML:
- Extracts YAML frontmatter for labels
- Extracts wiki links for later resolution
- Converts callout blocks to styled HTML
- Converts standard Markdown to HTML

### 3. **Upload**
The `trilium_uploader.py` uploads to Trilium:
- Creates folder notes for directories
- Creates text notes for Markdown files
- Adds labels from frontmatter
- Creates placeholder notes for missing wiki links
- Resolves all wiki links to Trilium reference links
- Creates relation attributes between linked notes

### 4. **Wiki Link Resolution**
Wiki links are processed in multiple passes:
1. **Orphans note creation**: Creates or finds an "Orphans" note to hold placeholder notes
2. **First pass**: Create all notes with placeholder spans for wiki links
3. **Second pass**: Create placeholder notes for missing wiki link targets (placed in Orphans folder)
4. **Third pass**: Replace placeholders with actual Trilium reference links

## Label Processing

Labels are extracted from frontmatter and support hierarchical categorization:

### Separator Rules:
- **Slash `/`**: Splits into name=value (e.g., `period/ancient-greek`)
- **Underscore `_`**: Splits into name=value (e.g., `category_ethics`)
- **No separator**: Creates label with no value (e.g., `philosophy`)

### Example:
```yaml
---
tags:
  - philosophy              # → #philosophy
  - period/ancient-greek    # → #period=ancient-greek
  - philosopher/aristotle   # → #philosopher=aristotle
  - theme/justice           # → #theme=justice
  - theme/polis             # → #theme=polis (multiple values allowed)
  - category_ethics         # → #category=ethics
---
```

All notes automatically receive the `#readOnly` label to prevent accidental editing.

## Callout Styling

The `.css` file contains Obsidian-style callout styling for rendering callouts with emoji icons and color-coded backgrounds.

### Automatic Upload (Recommended)

Use the included script to automatically upload the CSS to Trilium:

```bash
./upload_css.sh
```

This script will:
- Create a CSS code note titled "custom" (or update if it exists)
- Add the `#appCss` label automatically
- Apply the styling to all your notes

### Manual Upload (Alternative)

1. Open Trilium Notes
2. Create a new note with type "code"
3. Set the code language to "CSS"
4. Set the title to "custom"
5. Paste the entire content of `.css` file
6. Add label `#appCss` to the note

Callouts will then render with proper colors and emoji icons across all notes.

## Troubleshooting

### Authentication Errors
```
Error: 401 NOT_AUTHENTICATED
```
**Solution:** Check that your ETAPI token is valid and correctly set in `.env`

### Missing Notes
If wiki links don't resolve:
- Check that the target note exists in your Markdown directory
- Verify the note name matches (case-sensitive)
- Placeholder notes are automatically created in an "Orphans" folder
- The "Orphans" note is created automatically on first run (or reused if it exists)

### Callout Icons Not Showing
Make sure the `.css` file is uploaded to Trilium as a CSS note with `#appCss=enabled` label.

## Dependencies

- **trilium-py** (≥1.2.6) - Trilium Notes Python API client
- **markdown2** (≥2.4.0) - Markdown to HTML converter
- **PyYAML** (≥6.0) - YAML frontmatter parser
- **requests** (≥2.31.0) - HTTP library
- **beautifulsoup4** (≥4.12.0) - HTML processing

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## License

MIT License

## Acknowledgments

- [Trilium Notes](https://github.com/zadam/trilium) - Amazing note-taking application
- [Obsidian](https://obsidian.md) - Inspiration for callout syntax
- [markdown2](https://github.com/trentm/python-markdown2) - Markdown conversion

## Support

For issues or questions:
- Check the `test_docs/` directory for examples
- Review the `CLAUDE.md` file for technical details
- Open an issue on GitHub

---

**Made with ❤️ for Trilium Notes users who love Markdown**
