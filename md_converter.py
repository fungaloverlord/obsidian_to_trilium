"""Markdown to HTML converter for Trilium notes."""
import markdown2
import yaml
import re
from typing import Dict, Any, Tuple, Optional, List


class MarkdownConverter:
    """Converts Markdown content to HTML suitable for Trilium notes."""

    def __init__(self):
        """Initialize the converter with markdown2 extras."""
        self.extras = [
            'fenced-code-blocks',
            'tables',
            'strike',
            'task_list',
            'code-friendly',
            'header-ids',
            'footnotes',
            'cuddled-lists',
        ]

    def extract_wiki_links(self, markdown_content: str) -> List[str]:
        """
        Extract wiki-style links [[note_name]] or [[parent/note_name|display_text]] from Markdown content.

        Args:
            markdown_content: Raw markdown text

        Returns:
            List of referenced note names (without parent path or display text)
        """
        # Match [[note_name]] or [[parent/note_name|display_text]]
        wiki_link_pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
        matches = re.findall(wiki_link_pattern, markdown_content)

        result = []
        for match in matches:
            # If there's a / in the path, extract the note name after the last /
            if '/' in match:
                note_name = match.split('/')[-1].strip()
            else:
                note_name = match.strip()
            result.append(note_name)

        return result

    def extract_frontmatter(self, markdown_content: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Extract YAML frontmatter from Markdown content.

        Args:
            markdown_content: Raw markdown text with optional frontmatter

        Returns:
            Tuple of (frontmatter dict or None, markdown content without frontmatter)
        """
        # Match YAML frontmatter (--- at start, --- or ... at end)
        frontmatter_pattern = r'^---\s*\n(.*?)\n(?:---|\.\.\.)\s*\n'
        match = re.match(frontmatter_pattern, markdown_content, re.DOTALL)

        if match:
            frontmatter_text = match.group(1)
            content_without_frontmatter = markdown_content[match.end():]

            try:
                frontmatter = yaml.safe_load(frontmatter_text)
                return frontmatter, content_without_frontmatter
            except yaml.YAMLError as e:
                print(f"⚠️  Warning: Failed to parse YAML frontmatter: {e}")
                return None, markdown_content

        return None, markdown_content

    def convert_callouts(self, markdown_content: str) -> str:
        """
        Convert Markdown callout blocks to HTML aside elements.

        Supports formats like:
        > [!note]
        > Content here

        Or:
        > [!warning]
        > Content here

        Supported callout types: note, tip, important, caution, warning

        Args:
            markdown_content: Raw markdown text

        Returns:
            Markdown with callouts converted to HTML aside placeholders
        """
        # Allowed callout types (matching Obsidian + Trilium)
        ALLOWED_TYPES = {
            'note', 'abstract', 'summary', 'tldr', 'info', 'todo',
            'tip', 'hint', 'important', 'success', 'check', 'done',
            'question', 'help', 'faq', 'warning', 'caution', 'attention',
            'failure', 'fail', 'missing', 'danger', 'error', 'bug',
            'example', 'quote', 'cite'
        }

        # Map additional aliases to standard types
        TYPE_MAPPING = {
            # No additional mappings needed - all types directly supported
        }

        # Pattern to match callout blocks
        # Matches: > [!type] optional title
        #          > content line 1
        #          > content line 2
        callout_pattern = r'^>\s*\[!(\w+)\]([^\n]*)\n((?:^>.*\n?)*)'

        def replace_callout(match):
            callout_type = match.group(1).lower()
            title = match.group(2).strip()
            content_lines = match.group(3)

            # Map to allowed type or use default
            if callout_type in ALLOWED_TYPES:
                final_type = callout_type
            elif callout_type in TYPE_MAPPING:
                final_type = TYPE_MAPPING[callout_type]
            else:
                # Default to 'note' for unknown types
                final_type = 'note'
                print(f"  ⚠️  Unknown callout type '[!{callout_type}]', using 'note' instead")

            # Extract content from blockquote lines (remove leading > and space)
            content = '\n'.join(line[1:].lstrip() if line.startswith('>') else line
                               for line in content_lines.split('\n') if line.strip())

            # Convert wiki links in content to temporary markdown links BEFORE converting to HTML
            def wiki_to_temp_link(match):
                full_match = match.group(1)
                # Handle [[parent/note_name|display_text]] syntax
                if '|' in full_match:
                    note_path, display_text = full_match.split('|', 1)
                    note_path = note_path.strip()
                    display_text = display_text.strip()
                else:
                    note_path = full_match.strip()
                    display_text = note_path

                # Extract note name from path (part after last /)
                if '/' in note_path:
                    note_name = note_path.split('/')[-1].strip()
                else:
                    note_name = note_path

                return f'[{display_text}](WIKILINK:{note_name})'

            wiki_link_pattern = r'\[\[([^\]]+)\]\]'
            content_with_temp_links = re.sub(wiki_link_pattern, wiki_to_temp_link, content)

            # Convert the content markdown to HTML inline
            content_html = markdown2.markdown(content_with_temp_links, extras=self.extras).strip()

            # Convert temporary links to Trilium reference link placeholders
            def temp_to_trilium_placeholder(match):
                note_name = match.group(1)
                link_text = match.group(2)
                return f'<span data-wiki-link="{note_name}">{link_text}</span>'

            temp_link_pattern = r'<a href="WIKILINK:([^"]+)">([^<]+)</a>'
            content_html = re.sub(temp_link_pattern, temp_to_trilium_placeholder, content_html)

            # Build the aside element directly
            aside_html = f'<aside class="admon {final_type}">\n'
            if title:
                aside_html += f'    <p class="admon-title"><strong>{title}</strong></p>\n'
            aside_html += f'    {content_html}\n'
            aside_html += '</aside>'

            return aside_html

        return re.sub(callout_pattern, replace_callout, markdown_content, flags=re.MULTILINE)

    def convert(self, markdown_content: str) -> str:
        """
        Convert Markdown content to HTML.

        Args:
            markdown_content: Raw markdown text

        Returns:
            HTML string suitable for Trilium note content
        """
        # First convert callout blocks to HTML (before markdown processing)
        markdown_with_callouts = self.convert_callouts(markdown_content)

        # Convert wiki links to temporary markdown links
        # [[note_name]] -> [note_name](WIKILINK:note_name)
        # [[parent/note_name|display_text]] -> [display_text](WIKILINK:note_name)
        def wiki_to_temp_link(match):
            full_match = match.group(1)
            # Handle [[parent/note_name|display_text]] syntax
            if '|' in full_match:
                note_path, display_text = full_match.split('|', 1)
                note_path = note_path.strip()
                display_text = display_text.strip()
            else:
                note_path = full_match.strip()
                display_text = note_path

            # Extract note name from path (part after last /)
            if '/' in note_path:
                note_name = note_path.split('/')[-1].strip()
            else:
                note_name = note_path

            return f'[{display_text}](WIKILINK:{note_name})'

        wiki_link_pattern = r'\[\[([^\]]+)\]\]'
        markdown_with_temp_links = re.sub(wiki_link_pattern, wiki_to_temp_link, markdown_with_callouts)

        # Convert to HTML
        html = markdown2.markdown(markdown_with_temp_links, extras=self.extras)

        # Convert temporary links to Trilium reference links (will be updated later with actual note IDs)
        # <a href="WIKILINK:note_name">note_name</a> -> <span data-wiki-link="note_name">note_name</span>
        def temp_to_trilium_placeholder(match):
            note_name = match.group(1)
            link_text = match.group(2)
            return f'<span data-wiki-link="{note_name}">{link_text}</span>'

        temp_link_pattern = r'<a href="WIKILINK:([^"]+)">([^<]+)</a>'
        html = re.sub(temp_link_pattern, temp_to_trilium_placeholder, html)

        return html

    def convert_file(self, file_path: str) -> Tuple[str, Optional[Dict[str, Any]], List[str]]:
        """
        Read and convert a Markdown file to HTML, extracting frontmatter and wiki links.

        Args:
            file_path: Path to the .md file

        Returns:
            Tuple of (HTML string, frontmatter dict or None, list of wiki link references)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        frontmatter, content = self.extract_frontmatter(markdown_content)
        wiki_links = self.extract_wiki_links(content)
        html = self.convert(content)
        return html, frontmatter, wiki_links
